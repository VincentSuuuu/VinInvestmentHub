# Final Adversarial Audit - Vincent Investment Hub

Date: 2026-07-01  
Branch: `main`  
Scope: all pre-trial tasks except Memory Index recall and Reuters/RSSHub hardening, both deferred by user.
Notion archive: `https://app.notion.com/p/3903b3ced2278137b57af849ea399426`

## Final Verdict

The project is coherent enough for a several-day user trial. The operating model is now:

`External source -> Raw Signals -> user review -> Knowledge Items / My Output / Event Hubs`

This is the correct first-principles boundary. Raw Signals are inputs, not conclusions. Formal knowledge and personal thinking remain downstream of an explicit user decision.

There is one environment-level blocker: durable post-reboot scheduling cannot be completed from this Windows session because Task Scheduler, HKCU Run, and Startup shortcut persistence are all blocked or removed by policy. The current-session watcher is running, so the pilot can proceed while the Windows session stays active. A durable reboot-safe schedule still needs elevated Windows permission or a less restricted startup policy.

## Completed Since Last Audit

- Moved the full project history onto `main` without force-pushing over the old placeholder `main`.
- Kept `master` as an old branch; current work now tracks `origin/main`.
- Added `scripts/promote_raw_signal.py` for one-signal-at-a-time review actions.
- Added promotion support for `accept`, `output`, `merge`, `watch`, and `ignore`.
- Added safe duplicate refresh for Raw Signals still in `New`, `Needs Review`, or `Summarized`.
- Fixed UTF-8 BOM `.env` loading and current-working-directory `.env` resolution.
- Fixed RSS response decoding when feeds omit charset.
- Fixed runner JSON logs so downstream tools can parse them as UTF-8.
- Improved AI topic matching for CJK-adjacent ASCII terms and AI-specific names such as Anthropic, Claude, and 大模型.
- Refreshed the existing Anthropic Raw Signal in Notion so it now carries the `AI` topic.
- Added current-session watcher installation and verification.

## Verification Evidence

- Tests: `37 passed`, one third-party FastAPI/Starlette warning.
- Git: local branch `main` tracks `origin/main`.
- Notion: top page still uses three doors: Research Desk, Intelligence Middleware, System Console.
- Notion: homepage still keeps only four Live Working Views below the navigation section.
- Notion: `promote_raw_signal.py --list --limit 5 --json` returned active Raw Signals.
- Notion: `promote_raw_signal.py --raw-page-id 38f3b3ce-d227-8110-8300-fcce89e30da4 --action accept --dry-run --json` returned a valid dry-run without writing.
- Intake: manual runner wrote a UTF-8 log and duplicate protection reported existing rows instead of creating duplicates.
- Automation: watcher process is running in the current Windows session.

## Product/UX Audit

The Notion information architecture is now aligned with the user's actual workflow:

1. Homepage: decision/navigation surface.
2. Research Desk: daily work surface.
3. Intelligence Middleware: automation and candidate layer.
4. Core System: backend, database, rules, templates, and QA.

This hierarchy should stay fixed during the trial. The homepage should not receive new linked views unless one of the current four live views is removed. New operational views should go to Research Desk or Core System first.

Promotion UX is now good enough for pilot use because the helper requires a deliberate single-row action. That protects the knowledge base from accidental bulk promotion while removing the most repetitive manual work.

## Adversarial Findings

### P1 - Durable Scheduling Is Still Blocked By Windows Policy

The system can run twice daily while the current Windows session is active. It is not guaranteed after reboot/login because all normal persistence paths were blocked:

- Windows Task Scheduler: access denied.
- HKCU Run: access denied.
- Startup shortcut: creation did not persist under current policy.

This is not a code bug. It is an OS permission/policy boundary. The practical trial workaround is to keep the session active or manually start `scripts/watch_external_signal_schedule.ps1` after login.

### P2 - Memory Index Recall Is Still Deferred

This is intentionally not implemented in this pass per user instruction. No system page should claim ChatGPT/Codex recall is operational yet.

### P2 - Reuters/RSSHub Reliability Is Still Deferred

This is intentionally not hardened in this pass. Current fallback through Google News works for pilot discovery but should not be treated as production-grade Reuters ingestion.

### P2 - Source Scoring Still Needs Trial Feedback

The keyword model is now better, but it can still over-rank policy-adjacent tech or market items. This is acceptable for a 5-item-per-run candidate layer, but not for auto-promotion.

### P3 - Visual Screenshot Audit Was Not Performed

This final audit inspected Notion structure and content through the Notion connector, not live UI screenshots. It is enough for information architecture and workflow coherence, but not for pixel-level Notion visual polish.

### P3 - Old `master` Branch Still Exists

This is not a functional problem because `main` is now current and pushed. The old `master` branch can be deleted later after confirming GitHub default branch settings.

## Trial Readiness Checklist

- Homepage clarity: ready.
- Raw Signals intake: ready for current-session automation.
- Raw Signals dedupe: ready.
- Raw Signals refresh: ready for unprocessed candidates.
- Raw Signals promotion helper: ready.
- Knowledge base protection: ready; no auto-promotion.
- GitHub source alignment: ready on `main`.
- Three-way archive discipline: active.
- Memory Index recall: deferred.
- Reuters hardening: deferred.
- Durable post-reboot schedule: blocked by Windows policy.

## Recommended Trial Protocol

For the next 3-5 days:

1. Keep the Windows session active if you want the watcher to run automatically.
2. Review `候选信号 · 关键优先` once or twice a day.
3. Use the promotion helper only for signals you consciously accept, merge, watch, output, or ignore.
4. Note false positives, missed events, awkward tags, and promotion friction.
5. Do not expand source coverage until after this trial.

## Next Decision After Trial

After the trial, decide between:

1. Tighten scoring and tags first.
2. Make scheduling durable with admin/system permission.
3. Implement Memory Index recall.
4. Harden Reuters/RSSHub routes or replace them.
