from app.classifier import ClassificationProvider, classify_source
from app.models import SourceInput


class FakeProvider(ClassificationProvider):
    def classify(self, source):
        return {
            "source_type": "News",
            "theme": ["US-China Trade", "Bad Theme"],
            "geography": ["US", "China"],
            "asset_class": ["Macro"],
            "entities": ["Tariff"],
            "taxonomy_l1": ["Policy"],
            "taxonomy_l2": ["US-China Trade"],
            "taxonomy_l3": ["Tariff escalation"],
            "confidence": "Medium",
            "reason": "The source discusses tariff policy and market impact.",
            "needs_review": False,
        }


def test_classify_source_normalizes_known_taxonomy():
    source = SourceInput(title="Tariff update", url="https://example.com", text="New tariffs announced.")
    result = classify_source(source, FakeProvider())

    assert result.theme == ["US-China Trade"]
    assert result.geography == ["US", "China"]
    assert result.confidence == "Medium"
    assert result.classification_status == "Suggested"


class LowConfidenceProvider(ClassificationProvider):
    def classify(self, source):
        return {
            "source_type": "Research Report",
            "theme": [],
            "geography": [],
            "asset_class": [],
            "entities": [],
            "taxonomy_l1": [],
            "taxonomy_l2": [],
            "taxonomy_l3": [],
            "confidence": "Low",
            "reason": "The source has insufficient context.",
            "needs_review": True,
        }


def test_low_confidence_routes_to_needs_review():
    source = SourceInput(title="Unknown report", text="Fragment only.")
    result = classify_source(source, LowConfidenceProvider())

    assert result.classification_status == "Needs Review"
