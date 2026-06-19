from datetime import datetime, timezone

from app.models import ClassificationResult, SourceInput
from app.notion_client import build_source_properties


def test_build_source_properties_uses_suggested_fields_only():
    source = SourceInput(title="Tariff article", url="https://example.com", text="tariff text")
    result = ClassificationResult(
        source_type="News",
        theme=["US-China Trade"],
        geography=["US", "China"],
        asset_class=["Macro"],
        entities=["Tariff"],
        taxonomy_l1=["Policy"],
        taxonomy_l2=["US-China Trade"],
        taxonomy_l3=["Tariff escalation"],
        confidence="Medium",
        reason="Tariff policy source.",
        needs_review=False,
        classification_status="Suggested",
        classifier_run_at=datetime(2026, 6, 19, tzinfo=timezone.utc),
    )

    properties = build_source_properties(source, result)

    assert properties["Name"]["title"][0]["text"]["content"] == "Tariff article"
    assert properties["URL"]["url"] == "https://example.com"
    assert properties["Classification Status"]["select"]["name"] == "Suggested"
    assert properties["Suggested Theme"]["rich_text"][0]["text"]["content"] == "US-China Trade"
    assert "Theme" not in properties
    assert "Related Notes" not in properties
