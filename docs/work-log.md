# Vincent Investment Hub Work Log

This file records durable project checkpoints for local and GitHub history.
Each substantial work session should also be summarized on the Notion homepage/archive.

## 2026-07-01 Checkpoint

### Scope

- Correct project alignment after discovering the local Git remote still pointed to the abandoned source-classifier repository.
- Establish `docs/project-plan.md` as the local source plan checkpoint.
- Preserve Phase 6 external news intake implementation for Raw Signals.
- Add scripts for twice-daily external signal intake.

### Completed

- Added Phase 6 external source intake for Gelonghui, Caixin, and Reuters.
- Added Raw Signals Notion write support and duplicate-key protection.
- Added `世界宏观` taxonomy support in local classifier rules.
- Verified Notion token and Raw Signals write path.
- Verified duplicate protection with `created_count=0` and `skipped_existing_count=3` on repeated writes.
- Added local plan and scheduling scripts.

### Known Gaps

- Windows scheduled-task registration requires elevated PowerShell.
- Raw Signals promotion to Knowledge Items / My Output / Event Hubs is not automated.
- Memory Index retrieval into ChatGPT/Codex is not implemented.
- Reuters RSSHub routes are unstable and currently rely on fallback sources.

### Verification

- Latest local test run before this checkpoint: `27 passed`, with one third-party FastAPI/Starlette warning.
