# Adversarial Audit - Vincent Investment Hub

Date: 2026-07-01  
Scope: Notion product surface, local automation repo, GitHub alignment, Phase 6 intelligence middleware, and the project source plan.

## Executive Verdict

The rebuild direction is coherent after the homepage simplification and Phase 6 middleware work. The strongest current design choice is the separation between `Raw Signals` as a candidate layer and `Knowledge Items / My Output / Memory Index` as formal knowledge. This directly supports the goal of using external news as backup and context without polluting personal conclusions.

The main remaining risk is not database design. The main risk is operating discipline: some items are documented as designed but not yet implemented, and earlier Source Classifier artifacts still live beside the active VinInvestmentHub direction. The project now needs a strict source-of-truth and archive protocol so every Notion, local, and GitHub change stays aligned.

## Evidence Reviewed

- Notion top page: `Vincent Investment Hub`.
- Notion work pages: `Research Desk - 研究工作台`, `Vincent Investment Hub - Core System`, `Phase 6 Intelligence Middleware - 智能中间层`.
- Notion data layer: `候选信号 / Raw Signals` schema and views.
- Local docs: `README.md`, `docs/project-plan.md`, `docs/work-log.md`.
- Local automation: `scripts/fetch_external_signals.py`, scheduled-run scripts, external-source pipeline, filtering rules, Notion Raw Signals client.
- Git: `origin` now points to `https://github.com/VincentSuuuu/VinInvestmentHub.git`; `master` tracks `origin/master`; checkpoint commit `1d8cf51` was pushed.

## Findings

### P1 - Durable Automation Is Not Actually Installed

Phase 6.8 is script-ready but not system-scheduled. Windows Task Scheduler registration failed with access denied in the current environment, so the daily 08:30 and 20:30 runs are not yet durable.

Impact: The product plan can appear more automated than it really is. Raw Signals will not refresh by itself until the installer runs from elevated PowerShell or another scheduler is used.

Required correction: keep Phase 6.8 marked as `script ready; scheduler pending` until scheduled tasks are confirmed by task history or fresh Raw Signals writes.

### P1 - Source Of Truth Was Previously Split

Before this audit, the project plan existed across conversation, Notion pages, local files, and the wrong GitHub remote. The remote has now been corrected, but the operating rule needs to be enforced going forward.

Impact: Future work can become inconsistent even when individual tasks are correct.

Correction applied: `docs/project-plan.md` now requires every substantial work session to be archived in three places: local Markdown, Notion archive page, and GitHub commit/push.

### P2 - Legacy Source Classifier Still Shares The Repo

The repo still contains `Source Classifier MVP`, `VincentWorkPlaceVer2.0` references, and the original classifier web app. This can be useful as a local utility, but it is no longer the product direction.

Impact: New work can accidentally optimize the abandoned classifier direction instead of the active VinInvestmentHub system.

Correction applied: `docs/project-plan.md` now defines `VinInvestmentHub` as the active product direction and the classifier as a legacy/local utility.

### P2 - Raw Signals Promotion Is A Rule, Not A Workflow

Raw Signals has the right schema: `晋升动作`, `正式条目`, `相关旧观点`, topics, regions, importance, source, duplicate key. The Phase 6 page also defines Accept, Merge, Promote to Output, Watch, and Ignore. However, there is no one-click promotion script or Notion button automation in the local repo.

Impact: The system depends on manual consistency. Over time, useful signals may sit in candidate status without becoming formal knowledge or personal output.

Recommended correction: Phase 6 next implementation should be a small promotion helper before adding more sources.

### P2 - Memory Index Recall Is Designed But Not Implemented

The design correctly says Memory Index should only include formal content and approved personal views. There is not yet a local export/retrieval mechanism that lets ChatGPT/Codex reliably use it during future conversations.

Impact: The most valuable long-term promise, personal reasoning feeding back into future AI conversations, is not yet operational.

Recommended correction: build a minimal read-only Memory Index export/retrieval path after Raw Signals promotion is stable.

### P2 - README Environment Guidance Was Misleading

`README.md` previously told setup users to configure `NOTION_RAW_SIGNALS_DATA_SOURCE_ID`, while the current working path uses `NOTION_RAW_SIGNALS_DATABASE_ID`.

Impact: A future run could break Notion writes even though the token and database are valid.

Correction applied: README now names `NOTION_RAW_SIGNALS_DATABASE_ID` as the Raw Signals write path and scopes `NOTION_SOURCES_DATABASE_ID` to the legacy classifier.

### P2 - External Source Reliability Is Uneven

Gelonghui and Caixin can be tested through RSSHub plus Google News fallback. Reuters RSSHub routes are unstable and depend on fallback search when RSSHub returns 503 or times out.

Impact: Test data may over-rely on fallback search and underrepresent Reuters coverage.

Recommended correction: keep the source set small during QA, log source errors, and harden Reuters only after the first 3-5 day signal-quality review.

### P3 - Homepage Is Cleaner, But Needs A Hard Cap

The Notion homepage now has a clear top structure: `Research Desk`, `Intelligence Middleware`, and `System Console`, followed by four Live Working Views. This is a good correction from the earlier overloaded homepage.

Risk: if new views are added directly to the homepage, it will drift back into a dashboard pile.

Recommended correction: homepage rule should stay fixed at three doors plus four live views. Everything else belongs in Research Desk or Core System.

### P3 - Product Design Audit Evidence Was Structural, Not Screenshot-Based

This audit used fetched Notion page structure and database schema as evidence. It did not capture live screenshots of the Notion UI.

Impact: The audit can assess information architecture, naming, flow, and operating logic, but not pixel-level spacing, mobile rendering, or visual density.

Recommended correction: run a separate screenshot audit only if the next concern is visual polish rather than system coherence.

## Product Design Review

The current interaction model should stay simple:

1. Homepage answers: what matters now, and where do I work next?
2. Research Desk handles daily work: candidate signals, source cleanup, writing queue, active event hubs.
3. Core System handles backend: databases, templates, taxonomy, migration logs, QA, automation configuration.
4. Phase 6 handles middleware: Source Registry, Raw Signals, Memory Index, Automation Runs.

This is the right hierarchy. The user should not need to understand every database to create or classify a new page. The page should guide them by workflow state, not by raw database object.

The view naming rule is also correct: `对象 · 用途 · 状态/过滤条件`. It should be treated as a system invariant, not a design preference.

## Brainstorming Review Of The Source Plan

Recommended direction: keep the current B-first architecture.

- B-first means candidate automation first: external feeds enter Raw Signals, then the user decides what deserves promotion.
- Keep A-compatible architecture: sources can later become auto-promote eligible, but only after stable source quality, low duplication, high confidence, and clean QA.
- Do not expand sources yet. More sources before promotion and memory recall would increase noise and delay the real value loop.
- Next value loop should be: `Raw Signal -> user decision -> Knowledge Item / My Output -> Memory Index -> future Codex/ChatGPT recall`.

Rejected direction for now: full automatic news ingestion into formal knowledge. It is technically possible, but it would recreate the old classification confusion at a larger scale.

## Consistency Matrix

| Layer | Current State | Audit Judgment |
| --- | --- | --- |
| Notion homepage | Three-door navigation plus four live views; legacy views folded | Coherent, but keep the cap |
| Research Desk | Daily workflow is explicit and view naming rule is documented | Coherent |
| Core System | Backend directory, naming standard, layout rule, archives | Coherent |
| Phase 6 Notion page | Candidate-layer design and Memory Index boundary are clear | Coherent, implementation incomplete |
| Raw Signals schema | Supports duplicate key, source, suggested tags, promotion action, relations | Good enough for pilot |
| Local repo | Contains active Phase 6 tooling and legacy classifier | Needs boundary discipline |
| GitHub | Remote fixed to VinInvestmentHub and checkpoint pushed | Aligned as of `1d8cf51` |
| Archive process | Now documented in local plan and work log | New rule; must be enforced |

## Recommended Next Work

1. Confirm Phase 6.8 scheduling from elevated PowerShell or choose a user-level scheduler fallback.
2. Run the small-source feed for 3-5 days with 5 candidates per run.
3. Build the smallest useful promotion helper for Raw Signals.
4. Build a read-only Memory Index retrieval/export path.
5. After the system loop works, revisit source expansion and Reuters hardening.

## Completion Criteria For Future Work

A task is not complete until:

1. The Notion product surface reflects the change or has a dated archive note.
2. Local docs or implementation files reflect the change.
3. GitHub has a pushed commit for the same work.
4. The work log says what was tested and what remains blocked.
