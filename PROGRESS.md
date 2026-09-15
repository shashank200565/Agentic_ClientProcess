# Progress

## Current State
Phase 0 evaluation foundation is drafted and the initial Phase 1 backend foundation
is implemented through the extraction route. The first labeled workflow has now been
successfully extracted through a live OpenCode Go call.

## Completed
- [x] Product definition (PROJECT.md)
- [x] Architecture defined (ARCHITECTURE.md)
- [x] Task breakdown (TASKS.md)
- [x] 5 example investment management workflows drafted (trade confirmation matching, exposure limit check, mandate breach investigation, client onboarding suitability, quarterly performance reporting)
- [x] Phase 0 rubric with anchored 1-5 definitions (`eval/rubric.md`)
- [x] Initial labeled set with 15 workflows and 60 step labels (`eval/labeled_set.json`)
- [x] Evaluation script reporting exact agreement, within-one agreement, MAE, and verdict agreement (`eval/run_eval.py`)
- [x] Python 3.12 backend environment and dependency setup
- [x] Pydantic pipeline schemas (`backend/pipeline/schemas.py`)
- [x] SQLite schema and persistence helpers (`backend/db/schema.sql`, `backend/db/db.py`)
- [x] OpenCode Go client with structured JSON mode and model overrides (`backend/pipeline/llm_client.py`)
- [x] Structured extraction pipeline and `/analyze/extract` text/PDF route
- [x] Decision Engine scorer and `/analyze/score` route; mandate-breach workflow tested across 10 steps with persisted results
- [x] Local-only initial Git commit (`a86f143`)
- [x] Documentation scope updated for LangGraph orchestration, LangSmith observability, automation blueprints, static diagrams, and resumable workflow sessions
- [x] Frontend scaffold with real upload flow, placeholder step review scoring, and routed placeholder shells
- [x] Phase 3 automation blueprint and redesign generators with standalone routes, persisted structured outputs, and static diagrams
- [x] Phase 3 frontend integration with live scoring, generator actions, result views, and read-only diagrams
- [x] Phase 6 executive report endpoint and formatted frontend view with print-to-PDF support
- [x] Phase 4 LangGraph orchestration, LangSmith tracing hooks, and resumable WorkflowSession API
- [x] Portfolio dashboard aggregation endpoint, Recharts complexity/exception grid, derived step risk scoring, and bulletized text-heavy views
- [x] Interactive React Flow workflow map with fixed step nodes, click-to-inspect details, and note-aware scoped regeneration
- [x] Deterministic risk explanations added alongside every displayed risk score and label
- [x] Dagre-directed workflow map layout with fixed spacing, numbered nodes, capped summaries, and fit-to-view startup
- [x] Workflow map step navigation with animated centering, Previous/Next controls, and active-step highlighting
- [x] Decision Engine repetitiveness calibration rule evaluated across all 44 labeled steps; v3 verdict agreement reached 86.36%
- [x] Grounded screen assistant widget and `/analyze/screen-chat` explanation route tested with both model tiers
- [x] Before/after generated-output comparisons and in-session multi-turn screen-chat history
- [x] Screen assistant markdown rendering for bold, italics, inline code, and bullet responses
- [x] Custom hover tooltips added for all four step score dimensions in Step Review and workflow-map side panel
- [x] Persisted generator hydration and workflow-level Redesigned Flow browser view
- [x] Reworked frontend visual system around reusable blue gradient theme, verdict-first portfolio cards, focused step review, executive report hierarchy, and floating screen assistant
- [x] Frozen final extraction snapshot for all five demo workflows (`eval/final_extraction_snapshot.json`), aligned labeled descriptions, and completed the final 44-step eval at 81.82% verdict agreement (36/44)
- [x] Real resume-session listing with stage-aware continuation and deterministic automation copy
- [x] Automatic session upserts across extraction, scoring, and generation-complete transitions
- [x] Six-fix UI and Decision Engine polish batch, including stable boundary handling for mandate-breach step 3
- [x] Trade-confirmation extraction investigation: explicit extraction temperature=0.0 produced stable 7-step boundaries across three runs; fixed-step scoring still showed one verdict drift in three runs, and redesign generation reproduced successfully

## Currently Working On
Portfolio dashboard and risk presentation are complete. The five demo extraction
outputs are now frozen and must not be re-extracted; the aligned final evaluation
is 81.82% verdict agreement (36/44).

## Blocked
The API key is configured locally in `backend/.env` and is ignored by Git. Three
label-fit concerns remain flagged for review: trade-confirmation step 7,
onboarding steps 1-2 and 7, and quarterly data-review wording versus the original
labels. No labels were silently changed; descriptions were aligned word-for-word.

## Last OpenCode Report
Phase 2 Decision Engine implemented with fixed post-processing verdict logic; the
10-step `mandate_breach_investigation` route test persisted successfully. Full eval
has not been run.
