# Source Classifier MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Source Classifier MVP that suggests tags for new investment research sources and syncs suggested fields to Notion `Sources`.

**Architecture:** Use a small Python app with focused modules for taxonomy configuration, classification schema validation, LLM provider access, Notion payload mapping, and a lightweight local web UI. Keep the MVP conservative: write only suggested-classification fields and triage status back to Notion.

**Tech Stack:** Python 3 from the bundled Codex runtime, FastAPI, pytest, python-dotenv, official OpenAI Python SDK if available, Notion HTTP API, static HTML/CSS/JS.

---

## File Structure

- Create: `README.md` - local setup, environment variables, and run commands.
- Create: `.env.example` - required environment variable names without secrets.
- Create: `requirements.txt` - Python dependencies.
- Create: `app/main.py` - FastAPI app and route wiring.
- Create: `app/config.py` - environment loading and settings validation.
- Create: `app/taxonomy.py` - known taxonomy options and normalization helpers.
- Create: `app/models.py` - Pydantic request and response models.
- Create: `app/classifier.py` - provider-independent classification workflow.
- Create: `app/providers/openai_provider.py` - OpenAI-backed classifier provider.
- Create: `app/notion_client.py` - Notion API client for creating/updating source rows.
- Create: `app/static/index.html` - local review UI.
- Create: `app/static/styles.css` - restrained Notion-like interface styling.
- Create: `app/static/app.js` - browser interactions for classify, edit, and sync.
- Create: `tests/test_taxonomy.py` - taxonomy normalization tests.
- Create: `tests/test_classifier.py` - classification validation tests using a fake provider.
- Create: `tests/test_notion_client.py` - Notion payload mapping tests without live API calls.

## Task 1: Project Scaffold And Settings

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `README.md`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing settings test**

```python
# tests/test_config.py
import pytest

from app.config import Settings


def test_settings_require_notion_database_id():
    with pytest.raises(ValueError, match="NOTION_SOURCES_DATABASE_ID"):
        Settings(notion_token="secret", notion_sources_database_id="")


def test_settings_accept_required_values():
    settings = Settings(
        notion_token="secret",
        notion_sources_database_id="2383b3ce-d227-8225-92d4-8765979cd4a8",
        openai_api_key="key",
    )

    assert settings.notion_token == "secret"
    assert settings.notion_sources_database_id == "2383b3ce-d227-8225-92d4-8765979cd4a8"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_config.py -v
```

Expected: FAIL because `app.config` does not exist.

- [ ] **Step 3: Add project dependencies and config implementation**

```txt
# requirements.txt
fastapi
uvicorn
pydantic
python-dotenv
requests
pytest
openai
```

```text
# .env.example
NOTION_TOKEN=
NOTION_SOURCES_DATABASE_ID=2383b3ce-d227-8225-92d4-8765979cd4a8
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
```

```python
# app/__init__.py
```

```python
# app/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    notion_token: str
    notion_sources_database_id: str
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    def __post_init__(self):
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN is required")
        if not self.notion_sources_database_id:
            raise ValueError("NOTION_SOURCES_DATABASE_ID is required")


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        notion_token=os.getenv("NOTION_TOKEN", ""),
        notion_sources_database_id=os.getenv("NOTION_SOURCES_DATABASE_ID", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    )
```

```markdown
# Source Classifier MVP

Local classifier for `VincentWorkPlaceVer2.0` source triage.

## Setup

1. Copy `.env.example` to `.env`.
2. Set `NOTION_TOKEN`, `NOTION_SOURCES_DATABASE_ID`, and `OPENAI_API_KEY`.
3. Install dependencies:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn app.main:app --reload --port 8787
```
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_config.py -v
```

Expected: PASS.

## Task 2: Taxonomy Normalization

**Files:**
- Create: `app/taxonomy.py`
- Test: `tests/test_taxonomy.py`

- [ ] **Step 1: Write failing taxonomy tests**

```python
# tests/test_taxonomy.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_taxonomy.py -v
```

Expected: FAIL because `app.taxonomy` does not exist.

- [ ] **Step 3: Implement taxonomy normalization**

```python
# app/taxonomy.py
VALID_THEMES = {
    "US-China Trade",
    "China Macro",
    "US Macro",
    "Policy",
    "AI",
    "EV",
    "Healthcare",
    "Fiscal",
    "Monetary",
}

VALID_GEOGRAPHIES = {"China", "US", "Global", "Europe", "Asia"}

VALID_ASSET_CLASSES = {"Equity", "Bond", "FX", "Commodity", "Crypto", "Macro"}


def _clean_list(values):
    if not values:
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _filter_known(values, allowed):
    return [value for value in _clean_list(values) if value in allowed]


def normalize_suggestions(raw):
    return {
        "theme": _filter_known(raw.get("theme", []), VALID_THEMES),
        "geography": _filter_known(raw.get("geography", []), VALID_GEOGRAPHIES),
        "asset_class": _filter_known(raw.get("asset_class", []), VALID_ASSET_CLASSES),
        "entities": _clean_list(raw.get("entities", [])),
        "taxonomy_l1": _clean_list(raw.get("taxonomy_l1", [])),
        "taxonomy_l2": _clean_list(raw.get("taxonomy_l2", [])),
        "taxonomy_l3": _clean_list(raw.get("taxonomy_l3", [])),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_taxonomy.py -v
```

Expected: PASS.

## Task 3: Classification Workflow With Fake Provider

**Files:**
- Create: `app/models.py`
- Create: `app/classifier.py`
- Test: `tests/test_classifier.py`

- [ ] **Step 1: Write failing classifier tests**

```python
# tests/test_classifier.py
import pytest

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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_classifier.py -v
```

Expected: FAIL because `app.classifier` and `app.models` do not exist.

- [ ] **Step 3: Implement models and classification workflow**

```python
# app/models.py
from datetime import datetime, timezone
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
```

```python
# app/classifier.py
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
        confidence=confidence if confidence in {"High", "Medium", "Low"} else "Low",
        reason=str(raw.get("reason", "")).strip(),
        needs_review=needs_review,
        classification_status=status,
        classifier_run_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_classifier.py -v
```

Expected: PASS.

## Task 4: Notion Payload Mapping

**Files:**
- Create: `app/notion_client.py`
- Test: `tests/test_notion_client.py`

- [ ] **Step 1: Write failing Notion mapping test**

```python
# tests/test_notion_client.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_notion_client.py -v
```

Expected: FAIL because `app.notion_client` does not exist.

- [ ] **Step 3: Implement Notion mapping and client**

```python
# app/notion_client.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_notion_client.py -v
```

Expected: PASS.

## Task 5: OpenAI Provider

**Files:**
- Create: `app/providers/__init__.py`
- Create: `app/providers/openai_provider.py`
- Test: `tests/test_openai_provider.py`

- [ ] **Step 1: Write failing provider parsing test**

```python
# tests/test_openai_provider.py
from app.providers.openai_provider import parse_model_json


def test_parse_model_json_accepts_fenced_json():
    text = """```json
{"source_type":"News","theme":["Policy"],"geography":["US"],"asset_class":["Macro"],"entities":["Fed"],"taxonomy_l1":["Policy"],"taxonomy_l2":["Fed Policy"],"taxonomy_l3":[],"confidence":"High","reason":"Fed source.","needs_review":false}
```"""

    result = parse_model_json(text)

    assert result["source_type"] == "News"
    assert result["confidence"] == "High"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_openai_provider.py -v
```

Expected: FAIL because provider file does not exist.

- [ ] **Step 3: Implement provider with strict JSON prompt**

```python
# app/providers/__init__.py
```

```python
# app/providers/openai_provider.py
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
```

- [ ] **Step 4: Run provider test**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_openai_provider.py -v
```

Expected: PASS.

## Task 6: FastAPI Routes

**Files:**
- Create: `app/main.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write failing route test**

```python
# tests/test_api.py
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_route():
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_api.py -v
```

Expected: FAIL because `app.main` does not exist.

- [ ] **Step 3: Implement FastAPI shell**

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def create_app():
    app = FastAPI(title="Source Classifier MVP")

    @app.get("/api/health")
    def health():
        return {"ok": True}

    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
    return app


app = create_app()
```

- [ ] **Step 4: Run route test**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_api.py -v
```

Expected: PASS.

## Task 7: Static Review UI

**Files:**
- Create: `app/static/index.html`
- Create: `app/static/styles.css`
- Create: `app/static/app.js`

- [ ] **Step 1: Create static UI**

```html
<!-- app/static/index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Source Classifier</title>
    <link rel="stylesheet" href="/styles.css" />
  </head>
  <body>
    <main class="shell">
      <section class="panel">
        <p class="eyebrow">VincentWorkPlaceVer2.0</p>
        <h1>Source Classifier</h1>
        <label>Title <input id="title" /></label>
        <label>URL <input id="url" /></label>
        <label>Source Text <textarea id="text" rows="10"></textarea></label>
        <button id="classify">Analyze Source</button>
      </section>
      <section class="panel">
        <h2>Suggested Classification</h2>
        <pre id="result">{}</pre>
        <button id="sync" disabled>Sync to Notion</button>
      </section>
    </main>
    <script src="/app.js"></script>
  </body>
</html>
```

```css
/* app/static/styles.css */
:root {
  --bg: #f7f5f0;
  --ink: #181713;
  --muted: #68645c;
  --line: #ddd8cd;
  --panel: #fffdf8;
  --accent: #245f46;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.shell {
  display: grid;
  grid-template-columns: minmax(320px, 0.9fr) minmax(360px, 1.1fr);
  gap: 20px;
  max-width: 1120px;
  margin: 40px auto;
  padding: 0 20px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 20px;
}

.eyebrow {
  color: var(--muted);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

label {
  display: grid;
  gap: 6px;
  margin: 14px 0;
  color: var(--muted);
}

input,
textarea {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px;
  font: inherit;
  background: white;
  color: var(--ink);
}

button {
  border: 0;
  border-radius: 6px;
  background: var(--accent);
  color: white;
  padding: 10px 14px;
  font: inherit;
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

pre {
  white-space: pre-wrap;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 14px;
  min-height: 320px;
  background: #fbfaf6;
}

@media (max-width: 840px) {
  .shell {
    grid-template-columns: 1fr;
  }
}
```

```javascript
// app/static/app.js
let latestPayload = null;

document.getElementById("classify").addEventListener("click", async () => {
  const payload = {
    title: document.getElementById("title").value,
    url: document.getElementById("url").value,
    text: document.getElementById("text").value,
  };

  const response = await fetch("/api/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  latestPayload = await response.json();
  document.getElementById("result").textContent = JSON.stringify(latestPayload, null, 2);
  document.getElementById("sync").disabled = !response.ok;
});

document.getElementById("sync").addEventListener("click", async () => {
  if (!latestPayload) return;
  const response = await fetch("/api/sync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(latestPayload),
  });
  const result = await response.json();
  document.getElementById("result").textContent = JSON.stringify(result, null, 2);
});
```

- [ ] **Step 2: Verify static files are served**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn app.main:app --port 8787
```

Expected: opening `http://127.0.0.1:8787` shows the Source Classifier UI.

## Task 8: Wire Classify And Sync Endpoints

**Files:**
- Modify: `app/main.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Add failing tests for classify with fake provider injection**

```python
# append to tests/test_api.py
class RouteFakeProvider:
    def classify(self, source):
        return {
            "source_type": "News",
            "theme": ["US-China Trade"],
            "geography": ["US", "China"],
            "asset_class": ["Macro"],
            "entities": ["Tariff"],
            "taxonomy_l1": ["Policy"],
            "taxonomy_l2": ["US-China Trade"],
            "taxonomy_l3": ["Tariff escalation"],
            "confidence": "Medium",
            "reason": "Tariff policy source.",
            "needs_review": False,
        }


def test_classify_route_returns_suggestions():
    client = TestClient(create_app(classification_provider=RouteFakeProvider()))
    response = client.post(
        "/api/classify",
        json={"title": "Tariff update", "url": "https://example.com", "text": "Tariff policy update."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"]["title"] == "Tariff update"
    assert body["classification"]["theme"] == ["US-China Trade"]
    assert body["classification"]["classification_status"] == "Suggested"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_api.py -v
```

Expected: FAIL because `/api/classify` is missing.

- [ ] **Step 3: Implement endpoints with environment-backed provider**

```python
# replace app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.classifier import classify_source
from app.config import load_settings
from app.models import ClassificationResult, SourceInput
from app.notion_client import NotionClient
from app.providers.openai_provider import OpenAIProvider


def create_app(classification_provider=None):
    app = FastAPI(title="Source Classifier MVP")
    app.state.classification_provider = classification_provider

    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.post("/api/classify")
    def classify(source: SourceInput):
        try:
            provider = app.state.classification_provider
            if provider is None:
                settings = load_settings()
                provider = OpenAIProvider(settings.openai_api_key, settings.openai_model)
            result = classify_source(source, provider)
            return {"source": source.model_dump(), "classification": result.model_dump(mode="json")}
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post("/api/sync")
    def sync(payload: dict):
        try:
            settings = load_settings()
            source = SourceInput(**payload["source"])
            result = ClassificationResult(**payload["classification"])
            client = NotionClient(settings.notion_token, settings.notion_sources_database_id)
            return client.create_source(source, result)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
    return app


app = create_app()
```

- [ ] **Step 4: Run full test suite**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -v
```

Expected: PASS.

## Task 9: Notion Field Creation Outside Code

**Files:**
- No code files.
- Update Notion `Sources` database manually or through the Notion UI/API.

- [ ] **Step 1: Add fields to Notion `Sources`**

Add these properties to `Sources`:

```text
Classification Status: select
Suggested Theme: text
Suggested Geography: text
Suggested Asset Class: text
Suggested Entities: text
Suggested Taxonomy L1: text
Suggested Taxonomy L2: text
Suggested Taxonomy L3: text
Classification Confidence: select
Classification Reason: text
Classifier Run At: date
```

- [ ] **Step 2: Add select options**

For `Classification Status`:

```text
Unclassified
Suggested
Confirmed
Needs Review
```

For `Classification Confidence`:

```text
High
Medium
Low
```

- [ ] **Step 3: Create homepage linked views**

Create `Source Triage` views:

```text
Unclassified Sources: Classification Status is empty or Unclassified
Suggested, Waiting Confirmation: Classification Status is Suggested
Low Confidence: Classification Confidence is Low
Ready To Convert: Classification Status is Confirmed and Processing Status is not Linked
```

## Task 10: Final Local Verification

**Files:**
- No new files.

- [ ] **Step 1: Install dependencies**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -r requirements.txt
```

Expected: dependencies install successfully.

- [ ] **Step 2: Run all tests**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -v
```

Expected: PASS.

- [ ] **Step 3: Start local app**

Run:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn app.main:app --reload --port 8787
```

Expected: server starts on `http://127.0.0.1:8787`.

- [ ] **Step 4: Manual smoke test**

Open `http://127.0.0.1:8787`, paste a source, click `Analyze Source`, review JSON, then click `Sync to Notion`.

Expected: a new Notion `Sources` page is created with suggested classification fields populated and final taxonomy fields untouched.
