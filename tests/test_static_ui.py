from pathlib import Path


def test_review_form_has_editable_classification_fields():
    html = Path("app/static/index.html").read_text(encoding="utf-8")

    for field_id in [
        "source-type",
        "suggested-theme",
        "suggested-geography",
        "suggested-asset-class",
        "suggested-entities",
        "taxonomy-l1",
        "taxonomy-l2",
        "taxonomy-l3",
        "confidence",
        "classification-status",
        "classification-reason",
    ]:
        assert f'id="{field_id}"' in html


def test_review_form_has_status_and_raw_json_sections():
    html = Path("app/static/index.html").read_text(encoding="utf-8")

    assert 'id="status"' in html
    assert 'id="raw-json"' in html
