from app.taxonomy import normalize_suggestions


def test_normalize_removes_unknown_values():
    result = normalize_suggestions(
        {
            "theme": ["US-China Trade", "Unknown Theme"],
            "geography": ["US", "Mars"],
            "asset_class": ["Macro", "Private Credit"],
        }
    )

    assert result["theme"] == ["US-China Trade"]
    assert result["geography"] == ["US"]
    assert result["asset_class"] == ["Macro"]


def test_normalize_preserves_freeform_entities_and_taxonomy():
    result = normalize_suggestions(
        {
            "entities": ["Fed", "US Dollar"],
            "taxonomy_l1": ["Policy"],
            "taxonomy_l2": ["Fed Policy"],
            "taxonomy_l3": ["Rate cut timing"],
        }
    )

    assert result["entities"] == ["Fed", "US Dollar"]
    assert result["taxonomy_l1"] == ["Policy"]
    assert result["taxonomy_l2"] == ["Fed Policy"]
    assert result["taxonomy_l3"] == ["Rate cut timing"]
