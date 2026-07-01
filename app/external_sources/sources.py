from urllib.parse import urljoin
from urllib.parse import quote

from app.external_sources.models import SourceDefinition


def _rsshub_url(base_url: str, path: str) -> str:
    clean_base = base_url.rstrip("/") + "/"
    return urljoin(clean_base, path.lstrip("/"))


def _google_news_url(query: str, language: str = "zh-CN", region: str = "CN", ceid: str = "CN:zh-Hans") -> str:
    return f"https://news.google.com/rss/search?q={quote(query)}&hl={language}&gl={region}&ceid={quote(ceid)}"


def build_default_sources(rsshub_base_url: str = "https://rsshub.rssforever.com") -> dict[str, SourceDefinition]:
    return {
        "gelonghui": SourceDefinition(
            key="gelonghui",
            display_name="格隆汇 / Gelonghui",
            feed_urls=(
                _rsshub_url(rsshub_base_url, "/gelonghui/live"),
                _google_news_url("site:gelonghui.com (重大 OR 重磅 OR 突发 OR 关税 OR 制裁 OR 央行)"),
            ),
            trust="Medium",
            default_topics=("中国宏观", "政策"),
            default_regions=("中国", "全球"),
            source_registry_page_id="38c3b3ce-d227-81d5-9d46-fa698a1bc623",
        ),
        "caixin": SourceDefinition(
            key="caixin",
            display_name="财新网 / Caixin",
            feed_urls=(
                _rsshub_url(rsshub_base_url, "/caixin/latest"),
                _google_news_url("site:caixin.com (重大 OR 重磅 OR 突发 OR 关税 OR 制裁 OR 央行 OR 财政 OR 货币)"),
            ),
            trust="High",
            default_topics=("中国宏观", "政策"),
            default_regions=("中国",),
            source_registry_page_id="38c3b3ce-d227-81de-b679-d1e111ba95f3",
        ),
        "reuters": SourceDefinition(
            key="reuters",
            display_name="路透社 / Reuters",
            feed_urls=(
                _rsshub_url(rsshub_base_url, "/reuters/world/china?limit=20"),
                _rsshub_url(rsshub_base_url, "/reuters/world/us?limit=20"),
                _rsshub_url(rsshub_base_url, "/reuters/world/middle-east?limit=20"),
                _rsshub_url(rsshub_base_url, "/reuters/markets?limit=20"),
                _rsshub_url(rsshub_base_url, "/reuters/business/finance?limit=20"),
                _google_news_url(
                    "site:reuters.com (global economy OR IMF OR World Bank OR G7 OR G20 OR China OR United States OR Federal Reserve OR tariff OR sanctions OR Iran OR Israel OR oil OR central bank)",
                    language="en-US",
                    region="US",
                    ceid="US:en",
                ),
            ),
            trust="High",
            default_topics=("世界宏观", "美国宏观", "中国宏观", "政策"),
            default_regions=("全球", "中国", "美国"),
            source_registry_page_id="38c3b3ce-d227-81d1-b57f-fef5aa459802",
        ),
    }
