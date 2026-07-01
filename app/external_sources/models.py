from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SourceDefinition:
    key: str
    display_name: str
    feed_urls: tuple[str, ...]
    trust: str
    default_topics: tuple[str, ...] = ()
    default_regions: tuple[str, ...] = ()
    source_registry_page_id: str = ""


@dataclass(frozen=True)
class FeedItem:
    source_key: str
    source_name: str
    title: str
    url: str = ""
    summary: str = ""
    published_at: datetime | None = None
    raw_id: str = ""


@dataclass(frozen=True)
class ExternalSignal:
    source_key: str
    source_name: str
    title: str
    url: str
    summary: str
    published_at: datetime | None
    duplicate_key: str
    importance_score: int
    importance_label: str
    matched_terms: tuple[str, ...]
    suggested_topics: tuple[str, ...]
    suggested_regions: tuple[str, ...]
    suggested_asset_classes: tuple[str, ...]
    source_trust: str
    source_registry_page_id: str = ""
    ai_confidence: str = "Medium"
    entry_type: str = "新闻"
    notes: str = field(default="")
