from datetime import datetime, timezone
from typing import Protocol

from app.models import ClassificationResult, SourceInput
from app.taxonomy import normalize_suggestions


class ClassificationProvider(Protocol):
    def classify(self, source: SourceInput) -> dict:
        ...


def classify_source(source: SourceInput, provider: ClassificationProvider) -> ClassificationResult:
    raw = provider.classify(source)
    normalized = normalize_suggestions(raw)
    confidence = raw.get("confidence", "Low")
    if confidence not in {"High", "Medium", "Low"}:
        confidence = "Low"
    needs_review = bool(raw.get("needs_review")) or confidence == "Low"
    status = "Needs Review" if needs_review else "Suggested"

    return ClassificationResult(
        source_type=str(raw.get("source_type", "")).strip() or "Unknown",
        theme=normalized["theme"],
        geography=normalized["geography"],
        asset_class=normalized["asset_class"],
        entities=normalized["entities"],
        taxonomy_l1=normalized["taxonomy_l1"],
        taxonomy_l2=normalized["taxonomy_l2"],
        taxonomy_l3=normalized["taxonomy_l3"],
        confidence=confidence,
        reason=str(raw.get("reason", "")).strip(),
        needs_review=needs_review,
        classification_status=status,
        classifier_run_at=datetime.now(timezone.utc),
    )
