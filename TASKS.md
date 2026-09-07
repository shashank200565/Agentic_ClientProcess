# Tasks

## Current Phase: Phase 0 — Eval Foundation (do this before any pipeline code)

### Phase 0 — Ground Truth
- [x] Draft scoring rubric (`eval/rubric.md`) — anchored 1-5 definitions for repetitiveness, judgment need, compliance sensitivity, AI-suitability
- [x] Write out 15-20 investment management workflows as step lists (start with the 5 example flows already drafted: trade confirmation matching, exposure limit check, mandate breach investigation, client onboarding suitability review, quarterly performance reporting)
- [ ] Team independently scores each step against the rubric
- [ ] Reconcile disagreements → finalize `eval/labeled_set.json`
- [x] Write `eval/run_eval.py` — computes agreement (e.g. % exact/within-1 match, or weighted kappa) between engine output and labeled set

## Phase 1 — Backend Foundation

- [x] Define all Pydantic schemas in `backend/pipeline/schemas.py` (Workflow, WorkflowStep, StepScore, RedesignProposal)
- [x] Set up FastAPI app skeleton (`backend/api/main.py`) with health check route
- [x] Set up SQLite schema (`backend/db/schema.sql`) matching the Pydantic models
- [x] Build `backend/pipeline/llm_client.py` — single wrapper for OpenCode Go calls, configurable model per call
- [x] Implement `backend/pipeline/extraction.py` — document/text → `WorkflowStep[]`
- [x] Wire `/analyze/extract` route
- [ ] Test extraction against 3-4 of the labeled workflows — do the step boundaries look right?

## Phase 2 — Decision Engine (core IP — most human review, least agent delegation)

- [ ] Write first version of Decision Engine prompt against the rubric
- [ ] Implement `backend/pipeline/decision_engine.py` — `WorkflowStep` → `StepScore`
- [ ] Wire `/analyze/score` route
- [ ] Run `eval/run_eval.py` against labeled set — record baseline agreement %
- [ ] Iterate prompt, rerun eval, until agreement is acceptable (define target with mentor if possible)
- [ ] Document final verdict-decision logic (explicit rule combining 4 scores → verdict) in `DECISIONS.md`

## Phase 3 — Redesign Generator

- [ ] Implement `backend/pipeline/redesign.py` — `WorkflowStep` + `StepScore` (verdict=redesign) → `RedesignProposal`
- [ ] Wire `/analyze/redesign` route
- [ ] Sanity check: do generated redesigns look plausible for the investment management steps, not generic boilerplate?

## Phase 4 — Frontend (parallelizable with Phase 2/3)

- [ ] Scaffold React + Vite + Tailwind app
- [ ] Upload page → calls `/analyze/extract`
- [ ] Step review page → shows extracted steps, triggers `/analyze/score`, displays scores/reasoning/verdict color-coded
- [ ] Redesign view → shows `RedesignProposal` for flagged steps
- [ ] Portfolio Dashboard (Recharts) → complexity/exception grid across all analyzed workflows
- [ ] Wire all pages to real backend API (no mock data once backend routes exist)

## Phase 5 — Executive Report

- [ ] Design report template (consulting-style summary format)
- [ ] Implement report generation endpoint — templated from stored data, not a fresh open-ended LLM pass
- [ ] Export as PDF or formatted view

## Phase 6 — Integration, Polish, Demo Prep

- [ ] End-to-end test: upload → extract → score → redesign → dashboard → report, no manual intervention
- [ ] Deploy (or confirm local-demo fallback)
- [ ] Prepare demo script using the 5 investment management example workflows
- [ ] Rehearse Q&A: agreement score, cost model, "why not just a rules engine"

## Cut First If Behind Schedule
1. Chat Assistant (never started unless everything above is done)
2. Live deployment (fall back to local demo)
3. PDF export polish on Executive Report (plain formatted view is acceptable)
