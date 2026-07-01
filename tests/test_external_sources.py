from datetime import datetime, timezone

from app.external_sources.filtering import build_signal, score_importance
from app.external_sources.models import FeedItem
from app.external_sources.pipeline import collect_external_signals
from app.external_sources.rss import fetch_feed_xml, parse_feed_xml
from app.external_sources.sources import build_default_sources
from app.notion_raw_signals import RawSignalsNotionClient, build_raw_signal_properties, build_raw_signal_refresh_properties


def test_score_importance_keeps_major_policy_events():
    score, terms = score_importance("美国宣布对中国电动车加征关税，涉及出口管制和半导体。")

    assert score >= 6
    assert "关税" in terms
    assert "出口管制" in terms


def test_score_importance_filters_minor_market_noise():
    score, _ = score_importance("某公司盘中股价异动，涨幅扩大。")

    assert score < 3


def test_ascii_short_terms_use_word_boundaries():
    score, terms = score_importance("Fed's bubble blind spot is cause for anxiety.")

    assert score == 3
    assert "Fed" in terms
    assert "Xi" not in terms
    assert "war" not in terms


def test_ascii_terms_match_next_to_cjk_characters():
    score, terms = score_importance("Anthropic发布AI模型，美国政策限制解除。")

    assert score >= 5
    assert "AI" in terms


def test_parse_rss_feed_xml_for_caixin_item():
    source = build_default_sources()["caixin"]
    xml = """<?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>国务院宣布新的财政政策</title>
          <link>https://www.caixin.com/2026-06-27/101.html?utm_source=test</link>
          <description><![CDATA[政策将影响地方债和宏观需求。]]></description>
          <pubDate>Sat, 27 Jun 2026 02:00:00 GMT</pubDate>
          <guid>caixin-101</guid>
        </item>
      </channel>
    </rss>
    """

    items = parse_feed_xml(xml, source)

    assert len(items) == 1
    assert items[0].title == "国务院宣布新的财政政策"
    assert items[0].published_at.tzinfo == timezone.utc


def test_fetch_feed_xml_repairs_missing_charset_response(monkeypatch):
    class FakeResponse:
        encoding = "ISO-8859-1"
        apparent_encoding = "utf-8"

        def __init__(self):
            self.content = "央行宣布降息".encode("utf-8")

        def raise_for_status(self):
            return None

        @property
        def text(self):
            return self.content.decode(self.encoding)

    monkeypatch.setattr("app.external_sources.rss.requests.get", lambda *args, **kwargs: FakeResponse())

    assert fetch_feed_xml("https://example.com/rss") == "央行宣布降息"


def test_build_signal_infers_notion_options_and_duplicate_key():
    source = build_default_sources()["reuters"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="BREAKING: US announces new China tariff and export control package",
        url="https://www.reuters.com/world/us/example/?utm_campaign=x",
        summary="White House says the measures cover semiconductors and electric vehicles.",
    )

    signal = build_signal(item, source, min_score=3)

    assert signal is not None
    assert signal.importance_label == "关键"
    assert "中美贸易" in signal.suggested_topics
    assert "美国" in signal.suggested_regions
    assert "AI" not in signal.suggested_topics
    assert "欧洲" not in signal.suggested_regions
    assert signal.duplicate_key.startswith("reuters:")


def test_build_signal_infers_world_macro_for_global_events():
    source = build_default_sources()["reuters"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="IMF warns global economy faces renewed inflation risk",
        url="https://www.reuters.com/markets/global-economy",
        summary="Global markets are watching central bank policy and G20 coordination.",
    )

    signal = build_signal(item, source, min_score=3)

    assert signal is not None
    assert "世界宏观" in signal.suggested_topics
    assert "全球" in signal.suggested_regions
    assert "宏观" in signal.suggested_asset_classes


def test_export_control_without_us_context_is_not_us_china_trade():
    source = build_default_sources()["caixin"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="20家日企被列入中国出口管制清单",
        url="https://www.caixin.com/2026-06-29/102458626.html",
        summary="中国商务部表示，此举目的是制止日本相关军事实力提升。",
    )

    signal = build_signal(item, source, min_score=3)

    assert signal is not None
    assert "中国宏观" in signal.suggested_topics
    assert "中美贸易" not in signal.suggested_topics


def test_chinese_trump_policy_item_infers_us_macro_without_source_default():
    source = build_default_sources()["caixin"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="特朗普威胁对征收数字服务税的国家加征100%关税 欧洲首当其冲",
        url="https://www.caixin.com/2026-06-29/trump-tariff.html",
        summary="美国政策变化影响欧洲数字服务税谈判。",
    )

    signal = build_signal(item, source, min_score=3)

    assert signal is not None
    assert "美国宏观" in signal.suggested_topics
    assert "政策" in signal.suggested_topics
    assert "中国宏观" not in signal.suggested_topics


def test_anthropic_large_model_item_infers_ai_topic():
    source = build_default_sources()["caixin"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="Anthropic最强模型解除出口限制",
        url="https://www.caixin.com/2026-07-01/ai.html",
        summary="Claude大模型恢复访问，美国商务部移除限制。",
    )

    signal = build_signal(item, source, min_score=3)

    assert signal is not None
    assert "AI" in signal.suggested_topics


def test_collect_external_signals_deduplicates_with_fixture_fetcher():
    sources = build_default_sources()
    xml = """<rss version="2.0"><channel>
      <item>
        <title>BREAKING: Fed announces emergency rate cut</title>
        <link>https://www.reuters.com/markets/rates</link>
        <description>Federal Reserve decision affects global markets.</description>
      </item>
      <item>
        <title>Daily small cap shares rise</title>
        <link>https://www.reuters.com/markets/smallcap</link>
        <description>Minor market update.</description>
      </item>
    </channel></rss>"""

    signals = collect_external_signals(
        sources,
        source_keys=["reuters"],
        fetch_xml=lambda _: xml,
        min_score=3,
    )

    assert len(signals) == 1
    assert signals[0].title == "BREAKING: Fed announces emergency rate cut"


def test_collect_external_signals_filters_old_items_by_default_window():
    sources = build_default_sources()
    xml = """<rss version="2.0"><channel>
      <item>
        <title>BREAKING: Fed announces emergency rate cut</title>
        <link>https://www.reuters.com/markets/rates-old</link>
        <description>Federal Reserve decision affects global markets.</description>
        <pubDate>Mon, 01 Jun 2026 00:00:00 GMT</pubDate>
      </item>
    </channel></rss>"""

    signals = collect_external_signals(
        sources,
        source_keys=["reuters"],
        fetch_xml=lambda _: xml,
        min_score=3,
        max_age_days=14,
        now=datetime(2026, 6, 27, tzinfo=timezone.utc),
    )

    assert signals == []


def test_build_raw_signal_properties_matches_phase6_schema():
    source = build_default_sources()["gelonghui"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="央行宣布降息",
        url="https://www.gelonghui.com/news/1",
        summary="央行宣布降息，影响债券和人民币。",
    )
    signal = build_signal(item, source, min_score=3)

    properties = build_raw_signal_properties(signal)

    assert properties["信号标题"]["title"][0]["text"]["content"] == "央行宣布降息"
    assert properties["状态"]["select"]["name"] == "New"
    assert properties["建议重要性"]["select"]["name"] == "关键"
    assert {"name": "货币"} in properties["建议主题"]["multi_select"]
    assert properties["来源"]["relation"][0]["id"] == source.source_registry_page_id


def test_build_raw_signal_refresh_properties_preserves_status():
    source = build_default_sources()["gelonghui"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="央行宣布降息",
        url="https://www.gelonghui.com/news/1",
        summary="央行宣布降息，影响债券和人民币。",
    )
    signal = build_signal(item, source, min_score=3)

    properties = build_raw_signal_refresh_properties(signal)

    assert "状态" not in properties
    assert properties["信号标题"]["title"][0]["text"]["content"] == "央行宣布降息"


def test_raw_signals_client_skips_existing_duplicate_key(monkeypatch):
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return FakeResponse({"results": [{"id": "existing-page"}]})

    monkeypatch.setattr("app.notion_raw_signals.requests.post", fake_post)
    source = build_default_sources()["reuters"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="IMF warns global economy faces renewed inflation risk",
        url="https://www.reuters.com/markets/global-economy",
        summary="Global markets are watching central bank policy.",
    )
    signal = build_signal(item, source, min_score=3)
    client = RawSignalsNotionClient(token="secret", raw_signals_data_source_id="raw-ds")

    result = client.create_raw_signal(signal)

    assert result == {"existing": True, "page": {"id": "existing-page"}}
    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.notion.com/v1/data_sources/raw-ds/query"
    assert calls[0]["headers"]["Notion-Version"] == "2026-03-11"
    assert calls[0]["json"]["filter"]["rich_text"]["equals"] == signal.duplicate_key


def test_raw_signals_client_refreshes_existing_candidate(monkeypatch):
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append({"method": "post", "url": url, "json": json})
        return FakeResponse(
            {
                "results": [
                    {
                        "id": "existing-page",
                        "properties": {"状态": {"select": {"name": "New"}}},
                    }
                ]
            }
        )

    def fake_patch(url, headers, json, timeout):
        calls.append({"method": "patch", "url": url, "json": json})
        return FakeResponse({"id": "existing-page"})

    monkeypatch.setattr("app.notion_raw_signals.requests.post", fake_post)
    monkeypatch.setattr("app.notion_raw_signals.requests.patch", fake_patch)
    source = build_default_sources()["caixin"]
    item = FeedItem(
        source_key=source.key,
        source_name=source.display_name,
        title="Anthropic最强模型解除出口限制",
        url="https://www.caixin.com/2026-07-01/ai.html",
        summary="Claude大模型恢复访问，美国商务部移除限制。",
    )
    signal = build_signal(item, source, min_score=3)
    client = RawSignalsNotionClient(token="secret", raw_signals_database_id="raw-db")

    result = client.create_raw_signal(signal, refresh_existing=True)

    assert result["existing"] is True
    assert result["updated"] is True
    assert calls[1]["method"] == "patch"
    assert calls[1]["url"] == "https://api.notion.com/v1/pages/existing-page"
    assert "状态" not in calls[1]["json"]["properties"]
    assert {"name": "AI"} in calls[1]["json"]["properties"]["建议主题"]["multi_select"]
