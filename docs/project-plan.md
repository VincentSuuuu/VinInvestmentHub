# Vincent Investment Hub Project Plan

Last updated: 2026-07-01

## Source Of Truth

- Product workspace: Notion `Vincent Investment Hub`.
- Local implementation repo: `D:\Documents\NotionRebuild`.
- Current local remote: `https://github.com/VincentSuuuu/VinInvestmentHub.git`.
- This file is the local development plan checkpoint. GitHub is not current until local changes are committed and pushed.

## Working Rule

Before changing the system, check this plan, `README.md`, and `git status`.
Keep Notion as the product surface, and keep this repo as the automation/tooling surface.
Raw Signals remain a candidate layer unless a later phase explicitly promotes them.

## Phase Status

| Phase | Goal | Status |
| --- | --- | --- |
| Phase 1 | Rebuild direction, finance knowledge-base scope, legacy workspace review | Complete |
| Phase 2 | Core data architecture: Knowledge Items, Event Hubs, Taxonomy, Entities | Complete |
| Phase 3 | Homepage/Core System layout, view naming, display logic | Complete first pass |
| Phase 4 | Legacy material migration, missed-item review, relations and tags | Complete first pass |
| Phase 5 | Daily-use UX: simplified homepage, clear views, manual classification path | Complete first pass |
| Phase 6 | Intelligence middleware: external news intake, Raw Signals, Memory Index | In progress |
| Phase 7 | Stabilization, repo cleanup, GitHub handoff, long-term maintenance | Pending |

## Phase 6 Breakdown

| Task | Description | Status |
| --- | --- | --- |
| 6.1 | Small real-source test: Gelonghui, Caixin, Reuters | Complete |
| 6.2 | Major-event filtering, classification, dedupe into Raw Signals | Complete |
| 6.3 | Notion token/API write path | Complete |
| 6.4 | Duplicate-key write protection | Complete |
| 6.5 | `世界宏观` taxonomy and classification rule | Complete |
| 6.6 | Raw Signals promotion to Knowledge Items / My Output / Event Hubs | Rules defined, automation pending |
| 6.7 | Memory Index recall into ChatGPT/Codex conversations | Design direction defined, implementation pending |
| 6.8 | Scheduled external intake twice daily, 5 candidates per run | Script ready; system scheduler registration blocked by Windows permissions |
| 6.9 | 3-5 day real run QA and tuning | Pending |
| 6.10 | Reuters/RSSHub reliability hardening | Pending |

## Phase 6.8 Implementation Notes

- Runner script: `scripts/run_external_signal_intake.ps1`.
- Intended schedule: daily 08:30 and 20:30 Asia/Shanghai.
- Per run limit: `--max-candidates 5`.
- Output logs: `logs/external-signals/` (ignored by git).
- Admin installer: `scripts/install_external_signal_schedule.ps1`.
- Current environment blocked direct scheduler registration with access denied. Run the installer from an elevated PowerShell session to make the schedule durable.

## Next Tasks

1. Register or confirm the two daily scheduled tasks.
2. Let Raw Signals run for 3-5 days and review noise, missed events, tag quality, and source reliability.
3. Implement one-click or semi-automatic promotion from Raw Signals to Knowledge Items / My Output / Event Hubs.
4. Implement Memory Index retrieval/export so ChatGPT/Codex can use approved personal views and weekly conclusions.
5. Replace or harden unstable Reuters RSSHub routes.
6. Clean local repo changes, commit, and push to the intended GitHub repo.
