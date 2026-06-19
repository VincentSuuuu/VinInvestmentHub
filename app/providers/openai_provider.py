import json

from openai import OpenAI

from app.models import SourceInput


SYSTEM_PROMPT = """You classify investment research sources conservatively.
Return only JSON with keys:
source_type, theme, geography, asset_class, entities, taxonomy_l1, taxonomy_l2,
taxonomy_l3, confidence, reason, needs_review.
Prefer under-classification over over-classification.
Use confidence High, Medium, or Low.
Set needs_review true when uncertain."""


def parse_model_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


class OpenAIProvider:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def classify(self, source: SourceInput) -> dict:
        user_prompt = f"""Title: {source.title}
URL: {source.url}
Text:
{source.text}
"""
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return parse_model_json(response.output_text)
