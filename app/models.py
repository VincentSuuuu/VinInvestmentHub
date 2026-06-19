from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Confidence = Literal["High", "Medium", "Low"]
ClassificationStatus = Literal["Suggested", "Needs Review"]


class SourceInput(BaseModel):
    title: str = ""
    url: str = ""
    text: str = Field(default="", min_length=1)


class ClassificationResult(BaseModel):
    source_type: str
    theme: list[str]
    geography: list[str]
    asset_class: list[str]
    entities: list[str]
    taxonomy_l1: list[str]
    taxonomy_l2: list[str]
    taxonomy_l3: list[str]
    confidence: Confidence
    reason: str
    needs_review: bool
    classification_status: ClassificationStatus
    classifier_run_at: datetime
