# Tasks

## Current Phase: Phase 0 — Eval Foundation

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
- [x] Test extraction against 3-4 of the labeled workflows — verified against all 5 available real PDF workflows; step boundaries and structured outputs were sensible.

## Phase 2 — Decision Engine (core IP — most human review, least agent delegation)

- [x] Write first version of Decision Engine prompt against the rubric
- [x] Implement `backend/pipeline/decision_engine.py` — `WorkflowStep` → `StepScore`
- [x] Wire `/analyze/score` route
- [ ] Run `eval/run_eval.py` against labeled set — record baseline agreement %
- [ ] Iterate prompt, rerun eval, until agreement is acceptable (define target with mentor if possible)
- [ ] Document final verdict-decision logic (explicit rule combining 4 scores → verdict) in `DECISIONS.md`

## Phase 3 — Redesign & Automation Generators

- [ ] Implement `backend/pipeline/automation_blueprint.py` as a standalone function — `WorkflowStep` + `StepScore` (verdict=automate) → structured `AutomationBlueprint` using constrained templates for mechanism type (rules engine / RPA / scheduled job), trigger condition, rationale, and static visual workflow structure
- [ ] Wire `/analyze/automation-blueprint` route and test the standalone generator independently
- [ ] Sanity check: automation blueprints should be simpler, more templated, and conventional rather than another agentic/creative redesign
- [ ] Implement `backend/pipeline/redesign.py` as a standalone function — `WorkflowStep` + `StepScore` (verdict=redesign) → `RedesignProposal` with static visual workflow structure
- [ ] Wire `/analyze/redesign` route and test the standalone generator independently
- [ ] Sanity check: do generated redesigns look plausible for the investment management steps, not generic boilerplate?

## Phase 4 — Orchestration & Observability

- [ ] Set up LangGraph as the pipeline coordinator with conditional edges based on each step's verdict: `leave_as_is` → terminal, `automate` → existing Automation Blueprint Generator, `redesign` → existing Redesign Generator
- [ ] Define the LangGraph state model for current workflow stage, per-step verdicts, generated automation blueprints, generated redesigns, and static visual workflow structures
- [ ] Set up LangSmith tracing for all existing LLM calls in extraction and the Decision Engine as the first integration test
- [ ] Extend LangSmith tracing to the Automation Blueprint Generator and Redesign Generator, recording prompt, response, latency, model, and cost where available
- [ ] Add `WorkflowSession` persistence and API support for resuming the user's last incomplete workflow at the latest completed graph stage

## Phase 5 — Frontend (parallelizable with Phase 2/3/4)

- [x] Scaffold React + Vite + Tailwind app
- [x] Upload page → calls `/analyze/extract`
- [x] Step review page → shows extracted steps, with placeholder scores/reasoning/verdicts color-coded until `/analyze/score` exists
- [x] Automation Blueprint view shell → placeholder until the Automation Blueprint Generator and route exist
- [x] Redesign view shell → placeholder until the Redesign Generator and route exist
- [x] Session-resume UI shell → placeholder until `WorkflowSession` persistence and API support exist
- [x] Portfolio Dashboard shell → placeholder until analyzed workflow aggregation exists
- [ ] Wire all pages to real backend API (no mock data once backend routes exist)

## Phase 6 — Executive Report

- [ ] Design report template (consulting-style summary format)
- [ ] Implement report generation endpoint — templated from stored data, not a fresh open-ended LLM pass
- [ ] Export as PDF or formatted view

## Phase 7 — Integration, Polish, Demo Prep

- [ ] End-to-end test: upload → extract → score → redesign → dashboard → report, no manual intervention
- [ ] Deploy (or confirm local-demo fallback)
- [ ] Prepare demo script using the 5 investment management example workflows
- [ ] Rehearse Q&A: agreement score, cost model, "why not just a rules engine"

## Cut First If Behind Schedule
1. Chat Assistant (never started unless everything above is done)
2. Live deployment (fall back to local demo)
3. PDF export polish on Executive Report (plain formatted view is acceptable)

## Deferred / Not In Scope

- Live conversational editing of generated redesign and automation output
- Master routing agent for open-ended Q&A

These are future extensions, not rejected product ideas. This submission demonstrates
static generated output only.
