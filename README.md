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
