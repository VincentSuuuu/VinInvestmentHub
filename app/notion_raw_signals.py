import requests

from app.external_sources.models import ExternalSignal


DATABASE_NOTION_VERSION = "2022-06-28"
DATA_SOURCE_NOTION_VERSION = "2026-03-11"


def build_raw_signal_properties(signal: ExternalSignal):
    properties = {
        "信号标题": {"title": _title(signal.title)},
        "状态": {"select": {"name": "New"}},
        "来源名称": {"rich_text": _rich_text(signal.source_name)},
        "来源链接": {"url": signal.url or None},
        "原文摘要": {"rich_text": _rich_text(signal.summary)},
        "重复键": {"rich_text": _rich_text(signal.duplicate_key)},
        "来源可信度": {"select": {"name": signal.source_trust}},
        "AI置信度": {"select": {"name": signal.ai_confidence}},
        "建议主题": {"multi_select": _multi_select(signal.suggested_topics)},
        "建议地区": {"multi_select": _multi_select(signal.suggested_regions)},
        "建议资产类别": {"multi_select": _multi_select(signal.suggested_asset_classes)},
        "建议条目类型": {"select": {"name": signal.entry_type}},
        "建议重要性": {"select": {"name": signal.importance_label}},
        "处理备注": {"rich_text": _rich_text(signal.notes)},
    }
    if signal.published_at:
        properties["发布时间"] = {"date": {"start": signal.published_at.isoformat()}}
    if signal.source_registry_page_id:
        properties["来源"] = {"relation": [{"id": signal.source_registry_page_id}]}
    return properties


def build_raw_signal_refresh_properties(signal: ExternalSignal):
    properties = build_raw_signal_properties(signal)
    properties.pop("状态", None)
    return properties


class RawSignalsNotionClient:
    def __init__(
        self,
        token: str,
        raw_signals_data_source_id: str = "",
        raw_signals_database_id: str = "",
    ):
        self.token = token
        self.raw_signals_data_source_id = raw_signals_data_source_id
        self.raw_signals_database_id = raw_signals_database_id
        if not self.raw_signals_data_source_id and not self.raw_signals_database_id:
            raise ValueError("NOTION_RAW_SIGNALS_DATA_SOURCE_ID or NOTION_RAW_SIGNALS_DATABASE_ID is required")

    def create_raw_signal(self, signal: ExternalSignal, refresh_existing: bool = False):
        existing = self.find_existing_by_duplicate_key(signal.duplicate_key)
        if existing:
            if refresh_existing and _is_refreshable_existing(existing):
                return {
                    "existing": True,
                    "updated": True,
                    "page": self.refresh_existing_candidate(existing["id"], signal),
                }
            return {"existing": True, "page": existing}
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=self._headers(self._notion_version()),
            json={
                "parent": self._parent(),
                "properties": build_raw_signal_properties(signal),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def refresh_existing_candidate(self, page_id: str, signal: ExternalSignal):
        response = requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=self._headers(self._notion_version()),
            json={"properties": build_raw_signal_refresh_properties(signal)},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def find_existing_by_duplicate_key(self, duplicate_key: str):
        response = requests.post(
            self._query_url(),
            headers=self._headers(self._notion_version()),
            json={
                "filter": {
                    "property": "重复键",
                    "rich_text": {"equals": duplicate_key},
                },
                "page_size": 1,
            },
            timeout=30,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[0] if results else None

    def _parent(self):
        if self.raw_signals_data_source_id:
            return {"data_source_id": self.raw_signals_data_source_id}
        return {"database_id": self.raw_signals_database_id}

    def _query_url(self):
        if self.raw_signals_data_source_id:
            return f"https://api.notion.com/v1/data_sources/{self.raw_signals_data_source_id}/query"
        return f"https://api.notion.com/v1/databases/{self.raw_signals_database_id}/query"

    def _notion_version(self):
        if self.raw_signals_data_source_id:
            return DATA_SOURCE_NOTION_VERSION
        return DATABASE_NOTION_VERSION

    def _headers(self, notion_version: str):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": notion_version,
        }


def _title(value: str):
    return [{"type": "text", "text": {"content": _truncate(value or "Untitled signal", 200)}}]


def _rich_text(value: str):
    if not value:
        return []
    return [{"type": "text", "text": {"content": _truncate(value, 1900)}}]


def _multi_select(values: tuple[str, ...]):
    return [{"name": value} for value in values]


def _truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _is_refreshable_existing(page: dict) -> bool:
    status = (
        page.get("properties", {})
        .get("状态", {})
        .get("select", {})
        .get("name", "")
    )
    return status in {"New", "Needs Review", "Summarized"}
