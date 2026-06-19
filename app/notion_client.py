import requests

from app.models import ClassificationResult, SourceInput


def _rich_text(value: str):
    if not value:
        return []
    return [{"type": "text", "text": {"content": value}}]


def _join(values):
    return ", ".join(values)


def build_source_properties(source: SourceInput, result: ClassificationResult):
    title = source.title.strip() or source.url.strip() or "Untitled Source"
    return {
        "Name": {"title": [{"type": "text", "text": {"content": title}}]},
        "URL": {"url": source.url or None},
        "Classification Status": {"select": {"name": result.classification_status}},
        "Suggested Theme": {"rich_text": _rich_text(_join(result.theme))},
        "Suggested Geography": {"rich_text": _rich_text(_join(result.geography))},
        "Suggested Asset Class": {"rich_text": _rich_text(_join(result.asset_class))},
        "Suggested Entities": {"rich_text": _rich_text(_join(result.entities))},
        "Suggested Taxonomy L1": {"rich_text": _rich_text(_join(result.taxonomy_l1))},
        "Suggested Taxonomy L2": {"rich_text": _rich_text(_join(result.taxonomy_l2))},
        "Suggested Taxonomy L3": {"rich_text": _rich_text(_join(result.taxonomy_l3))},
        "Classification Confidence": {"select": {"name": result.confidence}},
        "Classification Reason": {"rich_text": _rich_text(result.reason)},
        "Classifier Run At": {"date": {"start": result.classifier_run_at.isoformat()}},
    }


class NotionClient:
    def __init__(self, token: str, sources_database_id: str):
        self.token = token
        self.sources_database_id = sources_database_id

    def create_source(self, source: SourceInput, result: ClassificationResult):
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            },
            json={
                "parent": {"database_id": self.sources_database_id},
                "properties": build_source_properties(source, result),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
