from app.notion_promotion import (
    RawSignalPromotionClient,
    build_knowledge_item_properties,
    build_raw_signal_promotion_properties,
    summarize_raw_signal,
)


def _raw_signal():
    return {
        "id": "raw-page",
        "properties": {
            "信号标题": {"title": [{"plain_text": "央行宣布降息"}]},
            "状态": {"select": {"name": "New"}},
            "来源名称": {"rich_text": [{"plain_text": "格隆汇 / Gelonghui"}]},
            "来源链接": {"url": "https://example.com/news"},
            "原文摘要": {"rich_text": [{"plain_text": "央行宣布降息，影响债券和人民币。"}]},
            "重复键": {"rich_text": [{"plain_text": "gelonghui:abc123"}]},
            "建议主题": {"multi_select": [{"name": "货币"}, {"name": "中国宏观"}]},
            "建议地区": {"multi_select": [{"name": "中国"}]},
            "建议资产类别": {"multi_select": [{"name": "债券"}, {"name": "宏观"}]},
            "建议条目类型": {"select": {"name": "新闻"}},
            "建议重要性": {"select": {"name": "关键"}},
            "发布时间": {"date": {"start": "2026-07-01T01:00:00+00:00"}},
            "处理备注": {"rich_text": [{"plain_text": "重大事件初筛 score=6"}]},
        },
    }


def test_build_knowledge_item_properties_maps_candidate_fields():
    props = build_knowledge_item_properties(_raw_signal(), role="资料源")

    assert props["标题"]["title"][0]["text"]["content"] == "央行宣布降息"
    assert props["内容角色"]["select"]["name"] == "资料源"
    assert props["状态"]["select"]["name"] == "待处理"
    assert props["重要性"]["select"]["name"] == "关键"
    assert props["条目类型"]["select"]["name"] == "新闻"
    assert {"name": "货币"} in props["主题"]["multi_select"]
    assert {"name": "中国"} in props["地区"]["multi_select"]
    assert {"name": "债券"} in props["资产类别"]["multi_select"]
    assert props["机构/来源"]["rich_text"][0]["text"]["content"] == "格隆汇 / Gelonghui"
    assert props["来源链接"]["url"] == "https://example.com/news"
    assert props["发布日期"]["date"]["start"] == "2026-07-01T01:00:00+00:00"


def test_build_raw_signal_promotion_properties_links_formal_item():
    props = build_raw_signal_promotion_properties(
        raw_signal=_raw_signal(),
        action="Accept to Knowledge",
        status="Promoted",
        knowledge_page_id="knowledge-page",
    )

    assert props["状态"]["select"]["name"] == "Promoted"
    assert props["晋升动作"]["select"]["name"] == "Accept to Knowledge"
    assert props["正式条目"]["relation"] == [{"id": "knowledge-page"}]
    assert "Promotion helper: Accept to Knowledge -> Promoted" in props["处理备注"]["rich_text"][0]["text"]["content"]


def test_summarize_raw_signal_for_review_queue():
    summary = summarize_raw_signal(_raw_signal())

    assert summary["id"] == "raw-page"
    assert summary["title"] == "央行宣布降息"
    assert summary["importance"] == "关键"
    assert summary["duplicate_key"] == "gelonghui:abc123"


def test_promote_to_knowledge_creates_and_updates(monkeypatch):
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
        return FakeResponse({"id": "knowledge-page"})

    def fake_patch(url, headers, json, timeout):
        calls.append({"method": "patch", "url": url, "json": json})
        return FakeResponse({"id": "raw-page"})

    monkeypatch.setattr("app.notion_promotion.requests.post", fake_post)
    monkeypatch.setattr("app.notion_promotion.requests.patch", fake_patch)
    client = RawSignalPromotionClient(
        token="secret",
        raw_signals_database_id="raw-db",
        knowledge_database_id="knowledge-db",
    )

    result = client.promote_to_knowledge(_raw_signal())

    assert result.status == "Promoted"
    assert result.knowledge_page_id == "knowledge-page"
    assert calls[0]["url"] == "https://api.notion.com/v1/pages"
    assert calls[0]["json"]["parent"] == {"database_id": "knowledge-db"}
    assert calls[1]["url"] == "https://api.notion.com/v1/pages/raw-page"
    assert calls[1]["json"]["properties"]["状态"]["select"]["name"] == "Promoted"
