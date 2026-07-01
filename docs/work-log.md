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

## 2026-07-01 Adversarial Audit Archive

### Scope

- Rechecked project alignment after correcting `origin` to `VincentSuuuu/VinInvestmentHub`.
- Audited Notion homepage, Research Desk, Core System, Phase 6 middleware, Raw Signals schema, local docs, scripts, and Git state for inconsistencies.
- Applied Product Design audit framing to the navigation/workflow surface and brainstorming framing to the source plan.

### Completed

- Confirmed local `origin` is `https://github.com/VincentSuuuu/VinInvestmentHub.git`.
- Confirmed `master` tracks `origin/master`.
- Confirmed top-level Notion page now uses three primary doors: Research Desk, Intelligence Middleware, and System Console.
- Confirmed Raw Signals schema contains `世界宏观`, promotion actions, duplicate key, and relations needed for the candidate-review loop.
- Corrected README setup guidance so Raw Signals writes use `NOTION_RAW_SIGNALS_DATABASE_ID`.
- Added the three-way archive rule to `docs/project-plan.md`.
- Added `docs/adversarial-audit-2026-07-01.md` as the local audit report.
- Created Notion archive page: `https://app.notion.com/p/3903b3ced2278138afbee8ad1a169646`.

### Open Findings

- Durable twice-daily Windows scheduling is still not registered because local scheduler APIs returned access denied without elevated PowerShell.
- Raw Signals promotion to Knowledge Items / My Output / Event Hubs remains a manual rule, not a one-click or automated workflow.
- Memory Index recall into ChatGPT/Codex remains designed but not implemented.
- Reuters/RSSHub reliability is still the weakest external-source dependency.

## 2026-07-01 Completion Pass

### Scope

- Finish remaining pre-trial tasks except Memory Index recall and Reuters/RSSHub hardening.
- Align GitHub primary branch to `main`.
- Make external intake usable during the trial period.
- Add a small Raw Signals promotion helper for manual review workflows.

### Completed

- Created and pushed `main` as the complete project branch without force-pushing over the old placeholder main.
- Kept `master` as an old branch for now; ongoing work uses `main`.
- Re-ran automation installation. Windows Task Scheduler still returned access denied.
- HKCU Run and Startup shortcut persistence were also blocked or removed by Windows policy.
- Verified watcher process is running in the current Windows session; durable post-reboot scheduling remains blocked by OS policy.
- Added `scripts/install_external_signal_automation.ps1` and `scripts/install_external_signal_watcher.ps1`.
- Fixed runner JSON logs to write UTF-8 instead of PowerShell UTF-16 redirection output.
- Added `scripts/promote_raw_signal.py` and `app/notion_promotion.py`.
- Promotion helper now supports `accept`, `output`, `merge`, `watch`, and `ignore` for one explicitly selected Raw Signal at a time.
- Fixed `.env` loading to support UTF-8 BOM and current-working-directory resolution.
- Fixed RSS response decoding when feeds omit charset.
- Improved AI topic detection for CJK-adjacent ASCII terms and AI-specific source terms such as Anthropic, Claude, and 大模型.
- Added safe refresh for duplicate Raw Signals that are still `New`, `Needs Review`, or `Summarized`.

### Verification

- Unit/integration tests: `37 passed`, with one third-party FastAPI/Starlette warning.
- Real Notion list check: `promote_raw_signal.py --list --limit 5 --json` returned active Raw Signals.
- Promotion dry-run check: `promote_raw_signal.py --raw-page-id 38f3b3ce-d227-8110-8300-fcce89e30da4 --action accept --dry-run --json` returned the expected action without writing.
- Manual intake runner check: latest UTF-8 log parsed successfully; duplicate protection reported `created_count=0`, `skipped_existing_count=4` after the first live run.
- Existing Anthropic Raw Signal was refreshed in place and now includes the `AI` topic.
- Final Notion audit page: `https://app.notion.com/p/3903b3ced2278137b57af849ea399426`.
- Final local audit report: `docs/final-adversarial-audit-2026-07-01.md`.

### Deferred By User

- Memory Index retrieval/export into ChatGPT/Codex.
- Reuters/RSSHub reliability hardening beyond current fallback behavior.
