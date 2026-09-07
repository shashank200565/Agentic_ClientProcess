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
- [x] Local-only initial Git commit (`a86f143`)

## Currently Working On
Phase 0 team scoring/reconciliation and broader extraction validation against 3-4
labeled workflows

## Blocked
None. The API key is configured locally in `backend/.env` and is ignored by Git.

## Last OpenCode Report
Phase 1 backend foundation implemented through extraction; first live extraction
verified for `trade_confirmation_matching`. No Decision Engine code was added.
