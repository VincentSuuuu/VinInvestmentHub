from app.notion_schema import build_sources_schema_properties


def test_build_sources_schema_properties_contains_suggested_fields():
    properties = build_sources_schema_properties()

    assert properties["Classification Status"]["select"]["options"] == [
        {"name": "Unclassified", "color": "gray"},
        {"name": "Suggested", "color": "blue"},
        {"name": "Confirmed", "color": "green"},
        {"name": "Needs Review", "color": "yellow"},
    ]
    assert properties["Suggested Theme"] == {"rich_text": {}}
    assert properties["Suggested Taxonomy L3"] == {"rich_text": {}}
    assert properties["Classification Confidence"]["select"]["options"] == [
        {"name": "High", "color": "green"},
        {"name": "Medium", "color": "yellow"},
        {"name": "Low", "color": "red"},
    ]
    assert properties["Classifier Run At"] == {"date": {}}


def test_build_sources_schema_properties_does_not_define_final_fields():
    properties = build_sources_schema_properties()

    assert "Theme" not in properties
    assert "Related Notes" not in properties
    assert "Related Events" not in properties
