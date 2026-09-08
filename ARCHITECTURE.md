# Architecture

## Stack

Backend:
- Python 3.12
- FastAPI (API layer)
- Pydantic v2 (schemas — every pipeline stage input/output is a Pydantic model, no exceptions)
- SQLite (storage — no ORM required initially; use `sqlite3` or SQLModel if the team prefers)
- pypdf / pdfplumber (document parsing)
- LangGraph (pipeline orchestration and verdict-conditional routing)

LLM layer:
- OpenCode Go subscription, OpenAI/Anthropic-compatible endpoint
- Model tiering: cheaper/faster model for Extraction (e.g. DeepSeek V4 Flash or similar), stronger reasoning model for Decision Engine and Redesign Generator (e.g. GLM-5.2 or Qwen3.7 Max — confirm current best available model in the Go roster before locking)
- All LLM calls go through structured output / tool-use mode. Never parse free-text LLM output with regex.
- LangSmith (observability for every LLM call: prompt, response, latency, model, and cost where available)

Frontend:
- React + Vite + TypeScript
- Tailwind CSS
- Recharts (dashboard visualizations)

Deployment:
- Frontend: Vercel
- Backend: Railway or Render
- (Local-only demo is an acceptable fallback if deployment adds risk close to the deadline — decide in Week 3, not now)

## Repository Structure

```
/backend
  /pipeline
     extraction.py        # Stage 1
     decision_engine.py    # Stage 2 — core IP, most iteration happens here
     automation_blueprint.py # Stage 3 — templated conventional automation output
     redesign.py           # Stage 3 — agent-first redesign output
     orchestration.py      # LangGraph coordinator and verdict-conditional edges
     schemas.py             # Shared Pydantic models, including WorkflowSession, AutomationBlueprint, and diagram data
     llm_client.py           # Single wrapper around OpenCode Go calls, model selection per stage
  /api
    main.py                # FastAPI app + routes
    routes/
      workflows.py
      analysis.py
      reports.py
      sessions.py            # Resume-last-workflow session endpoints
  /eval
    labeled_set.json        # Phase 0 ground truth (15-20 investment mgmt workflows)
    rubric.md                 # Explicit scoring rubric, anchored 1-5 scales
    run_eval.py                # Computes agreement between engine output and ground truth
  /db
     schema.sql              # Includes WorkflowSession persistence tables
   db.py
/frontend
  /src
    /pages
    /components
    /api                     # API client calls to backend
    /types                   # TypeScript types mirroring backend Pydantic schemas
/docs
  PROJECT.md
  ARCHITECTURE.md
  TASKS.md
  PROGRESS.md
  DECISIONS.md
  AGENTS.md
```

## Data Flow

1. User uploads a document → FastAPI stores raw file, creates a `Workflow` record (status=uploaded), and creates or resumes a `WorkflowSession`.
2. `/analyze/extract` → calls `pipeline/extraction.py` → structured `WorkflowStep[]` → stored, status=extracted; the LLM call is traced in LangSmith.
3. `/analyze/score` → calls `pipeline/decision_engine.py` per step → `StepScore` (4 dimensions + reasoning + verdict) → stored, status=analyzed; the LLM calls are traced in LangSmith.
4. The LangGraph pipeline coordinator receives each verdict and follows conditional graph edges:
   - `leave_as_is` → terminal path; no downstream generation stage.
   - `automate` → `pipeline/automation_blueprint.py` → structured `AutomationBlueprint` with a templated automation mechanism, trigger, rationale, and static visual workflow representation.
   - `redesign` → `pipeline/redesign.py` → structured `RedesignProposal` with an agent-first redesign and static visual workflow representation.
5. The coordinator persists graph/session state after each stage so a user can leave and resume at the current stage through the resume-last-session API.
6. Dashboard reads aggregate data across all `Workflow` records for the portfolio grid.
7. Report endpoint compiles a given workflow's steps, scores, automation blueprints, redesigns, and static diagrams into a formatted summary.

## Architecture Rules
- Business/LLM logic lives only in `/backend/pipeline` — never inline in route handlers
- Every pipeline function signature: `def run(input: PydanticModel) -> PydanticModel` — no exceptions, no stage returns raw dicts or strings
- Verdict routing is represented by a LangGraph graph with conditional edges; do not replace it with plain `if/elif` branching in a route or coordinator function.
- Frontend never calls the LLM directly — always through the backend API
- `llm_client.py` is the only file that knows about OpenCode Go specifics (base URL, model names, rate limit handling) — if the API provider changes, this is the only file that should need to change
- No stage's prompt template lives outside `/backend/pipeline` — do not scatter prompts across route files or frontend
- Every LLM call in extraction, Decision Engine, automation blueprint, and redesign stages must be traced through LangSmith, including prompt, response, latency, model used, and cost where available.
- `AutomationBlueprint` is a simpler, constrained, mostly templated generator for conventional automation; it is not a second creative agentic redesign call.
- `RedesignProposal` and `AutomationBlueprint` include read-only structured visual workflow data made of renderable nodes and edges; this is not an editable canvas.
- `WorkflowSession` is the persisted resumable state for the current stage, step verdicts, generated blueprints, and generated redesigns.
- Live conversational editing and a master routing agent for open-ended Q&A are deferred; only static generated output is in scope for this build.

## Model Tiering (confirm exact model names before Week 1 build starts)
- Extraction: cheap/fast model — this task is close to deterministic structuring
- Decision Engine: strongest available reasoning model — this is the stage that gets judged hardest
- Automation Blueprint Generator: no creative LLM call by default; use constrained templates/rules for mechanism, trigger, rationale, and diagram structure
- Redesign Generator: same tier as Decision Engine

## Orchestration and Session State

The pipeline coordinator is a LangGraph graph whose state includes the workflow,
current stage, per-step scores and verdicts, generated automation blueprints,
generated redesign proposals, and static visual representations. Conditional edges
route each step from the Decision Engine verdict to the appropriate terminal or
generator node. The graph state is checkpointed to the `WorkflowSession` table so
the API can resume the user's latest incomplete workflow at its last completed node.

## Static Visual Representation

Both downstream output schemas expose a read-only diagram structure suitable for
frontend rendering, such as `nodes` with stable IDs and labels and `edges` with
source, target, and optional labels. The representation is data for visualization,
not an editable workflow-builder model.

`AutomationBlueprint` also contains the constrained `mechanism_type` (`rules_engine`,
`rpa`, or `scheduled_job`), `trigger_condition`, and brief `rationale` fields.
`RedesignProposal` contains the agent-first redesign content and human-control
details. Both models share the static diagram contract but not the generation approach.
