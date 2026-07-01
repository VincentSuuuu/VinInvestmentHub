# Vincent Investment Hub Project Plan

Last updated: 2026-07-01

## Source Of Truth

- Product workspace: Notion `Vincent Investment Hub`.
- Local implementation repo: `D:\Documents\NotionRebuild`.
- Current local remote: `https://github.com/VincentSuuuu/VinInvestmentHub.git`.
- Primary Git branch: `main`.
- Latest archived checkpoint commit: `1d8cf51 Archive phase 6 intake checkpoint`.
- Main branch alignment commit: `0c451a7 Merge placeholder remote main into project history`.
- Latest Notion checkpoint page: `2026-07-01 Project Checkpoint - Phase 6 Archive`.
- Latest Notion audit page: `https://app.notion.com/p/3903b3ced2278138afbee8ad1a169646`.
- Final trial-readiness audit page: `https://app.notion.com/p/3903b3ced2278137b57af849ea399426`.
- This file is the local development plan checkpoint. GitHub is not current until local changes are committed and pushed.

## Working Rule

Before changing the system, check this plan, `README.md`, and `git status`.
Keep Notion as the product surface, and keep this repo as the automation/tooling surface.
Raw Signals remain a candidate layer unless a later phase explicitly promotes them.

Every substantial work session must be archived in three places before it is considered complete:

1. Local Markdown: update `docs/project-plan.md`, `docs/work-log.md`, or a dated report under `docs/`.
2. Notion: add a dated archive page under the top-level `Vincent Investment Hub` page or the relevant system page.
3. GitHub: commit and push the local archive to `VincentSuuuu/VinInvestmentHub`.

If one of the three archive targets is blocked, record the blocker in the local work log and do not mark the task fully complete.

## Phase Status

| Phase | Goal | Status |
| --- | --- | --- |
| Phase 1 | Rebuild direction, finance knowledge-base scope, legacy workspace review | Complete |
| Phase 2 | Core data architecture: Knowledge Items, Event Hubs, Taxonomy, Entities | Complete |
| Phase 3 | Homepage/Core System layout, view naming, display logic | Complete first pass |
| Phase 4 | Legacy material migration, missed-item review, relations and tags | Complete first pass |
| Phase 5 | Daily-use UX: simplified homepage, clear views, manual classification path | Complete first pass |
| Phase 6 | Intelligence middleware: external news intake, Raw Signals, Memory Index | In progress |
| Phase 7 | Stabilization, repo cleanup, GitHub handoff, long-term maintenance | Started |

## Phase 6 Breakdown

| Task | Description | Status |
| --- | --- | --- |
| 6.1 | Small real-source test: Gelonghui, Caixin, Reuters | Complete |
| 6.2 | Major-event filtering, classification, dedupe into Raw Signals | Complete |
| 6.3 | Notion token/API write path | Complete |
| 6.4 | Duplicate-key write protection | Complete |
| 6.5 | `世界宏观` taxonomy and classification rule | Complete |
| 6.6 | Raw Signals promotion to Knowledge Items / My Output / Event Hubs | Helper implemented for Accept / Output / Merge / Watch / Ignore |
| 6.7 | Memory Index recall into ChatGPT/Codex conversations | Deferred until post-trial |
| 6.8 | Scheduled external intake twice daily, 5 candidates per run | Current-session watcher running; durable persistence blocked by Windows policy |
| 6.9 | 3-5 day real run QA and tuning | Ready for user trial |
| 6.10 | Reuters/RSSHub reliability hardening | Deferred until post-trial |

## Phase 6.8 Implementation Notes

- Runner script: `scripts/run_external_signal_intake.ps1`.
- Intended schedule: daily 08:30 and 20:30 Asia/Shanghai.
- Per run limit: `--max-candidates 5`.
- Duplicate candidates still in `New`, `Needs Review`, or `Summarized` are refreshed so improved rules can update titles and suggested tags without changing user decisions.
- Output logs: `logs/external-signals/` (ignored by git).
- Runner JSON logs are written as UTF-8.
- Admin installer: `scripts/install_external_signal_schedule.ps1`.
- Unified installer: `scripts/install_external_signal_automation.ps1`.
- Current environment still blocks direct Task Scheduler registration with access denied.
- HKCU Run registration is also denied.
- Startup shortcut creation is removed by or blocked under current Windows policy.
- Current-session watcher is running and will execute during the 08:30-10:30 and 20:30-22:30 windows while this Windows session stays alive.
- Durable post-reboot scheduling still needs elevated Windows permissions or a different machine policy.

## Phase 6.6 Promotion Helper Notes

- CLI: `scripts/promote_raw_signal.py`.
- `accept`: creates a formal `Knowledge Items` page with role `资料源`, then marks the Raw Signal `Promoted`.
- `output`: creates a `我的输出` draft, then marks the Raw Signal `Promoted`.
- `merge`: links an existing Knowledge Item and marks the Raw Signal `Merged`.
- `watch`: optionally links an Event Hub and keeps the Raw Signal in `Needs Review`.
- `ignore`: marks the Raw Signal `Ignored`.
- The helper acts on one explicitly selected Raw Signal at a time. It does not auto-promote all incoming candidates.
- Live verification listed Raw Signals, dry-ran an Accept action, and refreshed the existing Anthropic candidate from `美国宏观` to `美国宏观 + AI` without creating a new row.

## Next Tasks

1. Register or confirm the two daily scheduled tasks.
2. Let Raw Signals run for 3-5 days and review noise, missed events, tag quality, and source reliability.
3. Use the promotion helper during the trial and tune the actions if any step feels awkward.
4. After trial, implement Memory Index retrieval/export so ChatGPT/Codex can use approved personal views and weekly conclusions.
5. After trial, replace or harden unstable Reuters RSSHub routes.
6. Keep all substantial work archived in Notion, local Markdown, and GitHub `main`.

## Architecture Boundary

- `VinInvestmentHub` is the active product direction.
- The earlier Source Classifier MVP remains in this repo as a legacy/local utility for classification review, not as the primary product surface.
- New automation should target Phase 6 Raw Signals and the Notion knowledge system first. Reuse legacy classifier modules only when they reduce duplication and do not reintroduce the old `VincentWorkPlaceVer2.0` direction.
