# VinInvestmentHub Local Tools

Local automation tools for the Notion investment research OS. The original source classifier is still available, and Phase 6 adds a candidate-only external news intake for Raw Signals.

Project plan checkpoint: `docs/project-plan.md`.
Current project audit: `docs/adversarial-audit-2026-07-01.md`.

## Setup

1. Copy `.env.example` to `.env`.
2. Set `NOTION_TOKEN` and `NOTION_RAW_SIGNALS_DATABASE_ID` for Raw Signals writes. Keep `NOTION_RAW_SIGNALS_DATA_SOURCE_ID` blank unless a future Notion data-source API path is explicitly enabled. Set `NOTION_SOURCES_DATABASE_ID` only when using the legacy Source Classifier, and set `OPENAI_API_KEY` only when running AI-assisted classification.
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

## Phase 6 External News Intake

The first test sources are:

- `gelonghui`: RSSHub `/gelonghui/live`, plus Google News site-search fallback
- `caixin`: RSSHub `/caixin/latest` without fulltext unlock, plus Google News site-search fallback
- `reuters`: RSSHub Reuters routes plus Google News site-search fallback because some public RSSHub instances return 503 for Reuters

Dry-run major event intake:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\fetch_external_signals.py --source all --json --max-candidates 10 --request-timeout 10
```

The default filter is `--min-score 5 --max-age-days 14 --max-candidates 10 --request-timeout 10`, so one ordinary keyword does not enter Raw Signals by itself and a test run stays reviewable.

Write candidates to Notion Raw Signals after `.env` is configured:

```powershell
C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\fetch_external_signals.py --source all --write-notion --max-candidates 10 --request-timeout 10
```

The Notion integration behind `NOTION_TOKEN` must be shared with the `Vincent Investment Hub` page or at least the `候选信号 / Raw Signals` database in Notion's Share / Connections menu. If it is not shared, the public Notion API returns `object_not_found` / 404 even when the token itself is valid.

The intake writes only candidate fields such as source, link, summary, duplicate key, suggested topic/region/asset class, and suggested importance. It does not promote content into formal Knowledge Items.
When Notion writes are enabled, the script checks Raw Signals by `重复键` first and reports already-existing rows as `skipped_existing_count`.

Raw Signals promotion stays simple during the test period:

- `Accept to Knowledge`: create or link a formal Knowledge Item, then set Raw Signal status to `Promoted`.
- `Merge with Existing`: attach the signal to an existing Knowledge Item or related old view, then set status to `Merged`.
- `Promote to Output`: use the signal as the starting point for a personal note, weekly summary, or report.
- `Watch`: keep it as an Event Hub input without polluting the formal knowledge base.
- `Ignore`: mark low-value duplicates or noisy market items as ignored.

`RSSHUB_BASE_URL` defaults to a public RSSHub instance that was reachable during setup. For production reliability, point it at a self-hosted RSSHub instance.

## Notion Homepage Views

After running the schema setup script, create a `Source Triage` section in the Notion homepage with linked `Sources` views:

- `Unclassified Sources`: `Classification Status` is empty or `Unclassified`
- `Suggested, Waiting Confirmation`: `Classification Status` is `Suggested`
- `Low Confidence`: `Classification Confidence` is `Low`
- `Ready To Convert`: `Classification Status` is `Confirmed` and `Processing Status` is not `Linked`
