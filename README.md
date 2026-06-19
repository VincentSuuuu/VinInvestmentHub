# Source Classifier MVP

Local classifier for `VincentWorkPlaceVer2.0` source triage.

## Setup

1. Copy `.env.example` to `.env`.
2. Set `NOTION_TOKEN`, `NOTION_SOURCES_DATABASE_ID`, and `OPENAI_API_KEY`.
3. Install dependencies:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -r requirements.txt
```

4. Add the suggested-classification fields to the Notion `Sources` database:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\setup_notion_sources_schema.py
```

## Run

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn app.main:app --reload --port 8787
```

Open `http://127.0.0.1:8787`.

## Notion Homepage Views

After running the schema setup script, create a `Source Triage` section in the Notion homepage with linked `Sources` views:

- `Unclassified Sources`: `Classification Status` is empty or `Unclassified`
- `Suggested, Waiting Confirmation`: `Classification Status` is `Suggested`
- `Low Confidence`: `Classification Confidence` is `Low`
- `Ready To Convert`: `Classification Status` is `Confirmed` and `Processing Status` is not `Linked`
