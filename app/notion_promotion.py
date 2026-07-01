from dataclasses import dataclass
from typing import Any

import requests


NOTION_VERSION = "2022-06-28"

RAW_ACTION_TO_STATUS = {
    "Accept to Knowledge": "Promoted",
    "Promote to Output": "Promoted",
    "Merge with Existing": "Merged",
    "Watch": "Needs Review",
    "Ignore": "Ignored",
}


@dataclass(frozen=True)
class PromotionResult:
    action: str
    raw_signal_page_id: str
    status: str
    knowledge_page_id: str = ""
    event_hub_page_id: str = ""


class RawSignalPromotionClient:
    def __init__(
        self,
        token: str,
        raw_signals_database_id: str,
        knowledge_database_id: str,
    ):
        self.token = token
        self.raw_signals_database_id = raw_signals_database_id
        self.knowledge_database_id = knowledge_database_id
        if not self.token:
            raise ValueError("NOTION_TOKEN is required")
        if not self.raw_signals_database_id:
            raise ValueError("NOTION_RAW_SIGNALS_DATABASE_ID is required")
        if not self.knowledge_database_id:
            raise ValueError("NOTION_KNOWLEDGE_DATABASE_ID is required")

    def list_review_queue(self, limit: int = 10) -> list[dict[str, Any]]:
        response = requests.post(
            f"https://api.notion.com/v1/databases/{self.raw_signals_database_id}/query",
            headers=self._headers(),
            json={
                "filter": {
                    "or": [
                        {"property": "状态", "select": {"equals": "New"}},
                        {"property": "状态", "select": {"equals": "Needs Review"}},
                    ]
                },
                "sorts": [{"property": "发布时间", "direction": "descending"}],
                "page_size": limit,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("results", [])

    def get_raw_signal(self, page_id: str) -> dict[str, Any]:
        response = requests.get(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def find_raw_signal_by_duplicate_key(self, duplicate_key: str) -> dict[str, Any] | None:
        response = requests.post(
            f"https://api.notion.com/v1/databases/{self.raw_signals_database_id}/query",
            headers=self._headers(),
            json={
                "filter": {"property": "重复键", "rich_text": {"equals": duplicate_key}},
                "page_size": 1,
            },
            timeout=30,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[0] if results else None

    def promote_to_knowledge(self, raw_signal: dict[str, Any]) -> PromotionResult:
        knowledge_page = self.create_knowledge_item(raw_signal, role="资料源")
        return self.update_raw_signal(
            raw_signal=raw_signal,
            action="Accept to Knowledge",
            knowledge_page_id=knowledge_page["id"],
        )

    def promote_to_output(self, raw_signal: dict[str, Any]) -> PromotionResult:
        knowledge_page = self.create_knowledge_item(
            raw_signal,
            role="我的输出",
            entry_type="随想",
            status="Inbox",
        )
        return self.update_raw_signal(
            raw_signal=raw_signal,
            action="Promote to Output",
            knowledge_page_id=knowledge_page["id"],
        )

    def merge_with_existing(self, raw_signal: dict[str, Any], knowledge_page_id: str) -> PromotionResult:
        if not knowledge_page_id:
            raise ValueError("knowledge_page_id is required for Merge with Existing")
        return self.update_raw_signal(
            raw_signal=raw_signal,
            action="Merge with Existing",
            knowledge_page_id=knowledge_page_id,
        )

    def watch(self, raw_signal: dict[str, Any], event_hub_page_id: str = "") -> PromotionResult:
        return self.update_raw_signal(
            raw_signal=raw_signal,
            action="Watch",
            event_hub_page_id=event_hub_page_id,
        )

    def ignore(self, raw_signal: dict[str, Any]) -> PromotionResult:
        return self.update_raw_signal(raw_signal=raw_signal, action="Ignore")

    def create_knowledge_item(
        self,
        raw_signal: dict[str, Any],
        role: str,
        entry_type: str | None = None,
        status: str = "待处理",
    ) -> dict[str, Any]:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=self._headers(),
            json={
                "parent": {"database_id": self.knowledge_database_id},
                "properties": build_knowledge_item_properties(raw_signal, role, entry_type, status),
                "children": build_knowledge_item_children(raw_signal),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def update_raw_signal(
        self,
        raw_signal: dict[str, Any],
        action: str,
        knowledge_page_id: str = "",
        event_hub_page_id: str = "",
    ) -> PromotionResult:
        status = RAW_ACTION_TO_STATUS[action]
        response = requests.patch(
            f"https://api.notion.com/v1/pages/{raw_signal['id']}",
            headers=self._headers(),
            json={
                "properties": build_raw_signal_promotion_properties(
                    raw_signal=raw_signal,
                    action=action,
                    status=status,
                    knowledge_page_id=knowledge_page_id,
                    event_hub_page_id=event_hub_page_id,
                )
            },
            timeout=30,
        )
        response.raise_for_status()
        return PromotionResult(
            action=action,
            raw_signal_page_id=raw_signal["id"],
            status=status,
            knowledge_page_id=knowledge_page_id,
            event_hub_page_id=event_hub_page_id,
        )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }


def build_knowledge_item_properties(
    raw_signal: dict[str, Any],
    role: str,
    entry_type: str | None = None,
    status: str = "待处理",
) -> dict[str, Any]:
    props = raw_signal.get("properties", {})
    title = _title_text(props.get("信号标题")) or "Untitled raw signal"
    source_name = _rich_text(props.get("来源名称"))
    source_url = _url(props.get("来源链接"))
    summary = _rich_text(props.get("原文摘要"))
    topics = _multi_select_names(props.get("建议主题"))
    regions = _multi_select_names(props.get("建议地区"))
    asset_classes = _multi_select_names(props.get("建议资产类别"))
    importance = _select_name(props.get("建议重要性")) or "重要"
    inferred_entry_type = entry_type or _select_name(props.get("建议条目类型")) or "新闻"
    published_at = _date_start(props.get("发布时间"))

    knowledge_props = {
        "标题": {"title": _title(title)},
        "内容角色": {"select": {"name": role}},
        "状态": {"select": {"name": status}},
        "重要性": {"select": {"name": importance}},
        "条目类型": {"select": {"name": inferred_entry_type}},
        "主题": {"multi_select": _multi_select(topics)},
        "地区": {"multi_select": _multi_select(regions)},
        "资产类别": {"multi_select": _multi_select(asset_classes)},
        "机构/来源": {"rich_text": _rich_text_value(source_name)},
        "来源链接": {"url": source_url or None},
        "摘要": {"rich_text": _rich_text_value(summary)},
    }
    if published_at:
        knowledge_props["发布日期"] = {"date": {"start": published_at}}
    return knowledge_props


def build_raw_signal_promotion_properties(
    raw_signal: dict[str, Any],
    action: str,
    status: str,
    knowledge_page_id: str = "",
    event_hub_page_id: str = "",
) -> dict[str, Any]:
    props = raw_signal.get("properties", {})
    existing_note = _rich_text(props.get("处理备注"))
    note = f"Promotion helper: {action} -> {status}"
    combined_note = f"{existing_note}\n{note}".strip() if existing_note else note
    update = {
        "状态": {"select": {"name": status}},
        "晋升动作": {"select": {"name": action}},
        "处理备注": {"rich_text": _rich_text_value(combined_note)},
    }
    if knowledge_page_id:
        update["正式条目"] = {"relation": [{"id": knowledge_page_id}]}
    if event_hub_page_id:
        update["建议关联专题"] = {"relation": [{"id": event_hub_page_id}]}
    return update


def build_knowledge_item_children(raw_signal: dict[str, Any]) -> list[dict[str, Any]]:
    props = raw_signal.get("properties", {})
    source_name = _rich_text(props.get("来源名称")) or "Unknown source"
    source_url = _url(props.get("来源链接")) or ""
    summary = _rich_text(props.get("原文摘要")) or "No summary provided."
    duplicate_key = _rich_text(props.get("重复键")) or ""
    notes = _rich_text(props.get("处理备注")) or ""
    lines = [
        ("Source", source_name),
        ("URL", source_url),
        ("Raw Signal Duplicate Key", duplicate_key),
    ]
    if notes:
        lines.append(("Raw Notes", notes))
    children = [
        _paragraph("Created from Raw Signals promotion helper."),
        _paragraph(" | ".join(f"{label}: {value}" for label, value in lines if value)),
        _paragraph(summary),
    ]
    return children


def summarize_raw_signal(raw_signal: dict[str, Any]) -> dict[str, Any]:
    props = raw_signal.get("properties", {})
    return {
        "id": raw_signal.get("id", ""),
        "title": _title_text(props.get("信号标题")),
        "status": _select_name(props.get("状态")),
        "importance": _select_name(props.get("建议重要性")),
        "topics": _multi_select_names(props.get("建议主题")),
        "source": _rich_text(props.get("来源名称")),
        "duplicate_key": _rich_text(props.get("重复键")),
        "url": _url(props.get("来源链接")),
    }


def _title(value: str):
    return [{"type": "text", "text": {"content": _truncate(value, 200)}}]


def _rich_text_value(value: str):
    if not value:
        return []
    return [{"type": "text", "text": {"content": _truncate(value, 1900)}}]


def _multi_select(values: list[str]):
    return [{"name": value} for value in values if value]


def _paragraph(value: str):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": _rich_text_value(value)},
    }


def _title_text(prop: dict[str, Any] | None) -> str:
    if not prop:
        return ""
    return "".join(part.get("plain_text", "") for part in prop.get("title", []))


def _rich_text(prop: dict[str, Any] | None) -> str:
    if not prop:
        return ""
    return "".join(part.get("plain_text", "") for part in prop.get("rich_text", []))


def _select_name(prop: dict[str, Any] | None) -> str:
    if not prop or not prop.get("select"):
        return ""
    return prop["select"].get("name", "")


def _multi_select_names(prop: dict[str, Any] | None) -> list[str]:
    if not prop:
        return []
    return [item.get("name", "") for item in prop.get("multi_select", []) if item.get("name")]


def _url(prop: dict[str, Any] | None) -> str:
    if not prop:
        return ""
    return prop.get("url") or ""


def _date_start(prop: dict[str, Any] | None) -> str:
    if not prop or not prop.get("date"):
        return ""
    return prop["date"].get("start", "")


def _truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1] + "…"
