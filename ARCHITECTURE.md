# Architecture

## Stack

Backend:
- Python 3.12
- FastAPI (API layer)
- Pydantic v2 (schemas — every pipeline stage input/output is a Pydantic model, no exceptions)
- SQLite (storage — no ORM required initially; use `sqlite3` or SQLModel if the team prefers)
- pypdf / pdfplumber (document parsing)

LLM layer:
- OpenCode Go subscription, OpenAI/Anthropic-compatible endpoint
- Model tiering: cheaper/faster model for Extraction (e.g. DeepSeek V4 Flash or similar), stronger reasoning model for Decision Engine and Redesign Generator (e.g. GLM-5.2 or Qwen3.7 Max — confirm current best available model in the Go roster before locking)
- All LLM calls go through structured output / tool-use mode. Never parse free-text LLM output with regex.

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
    redesign.py           # Stage 3
    schemas.py             # Shared Pydantic models for all stages
    llm_client.py           # Single wrapper around OpenCode Go calls, model selection per stage
  /api
    main.py                # FastAPI app + routes
    routes/
      workflows.py
      analysis.py
      reports.py
  /eval
    labeled_set.json        # Phase 0 ground truth (15-20 investment mgmt workflows)
    rubric.md                 # Explicit scoring rubric, anchored 1-5 scales
    run_eval.py                # Computes agreement between engine output and ground truth
  /db
    schema.sql
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

1. User uploads document → FastAPI stores raw file, creates `Workflow` record (status=uploaded)
2. `/analyze/extract` → calls `pipeline/extraction.py` → structured `WorkflowStep[]` → stored, status=extracted
3. `/analyze/score` → calls `pipeline/decision_engine.py` per step → `StepScore` (4 dimensions + reasoning + verdict) → stored, status=analyzed
4. For steps with verdict="redesign" → `/analyze/redesign` → calls `pipeline/redesign.py` → `RedesignProposal` → stored
5. Dashboard reads aggregate data across all `Workflow` records for the portfolio grid
6. Report endpoint compiles a given workflow's steps + scores + redesigns into a formatted summary

## Architecture Rules
- Business/LLM logic lives only in `/backend/pipeline` — never inline in route handlers
- Every pipeline function signature: `def run(input: PydanticModel) -> PydanticModel` — no exceptions, no stage returns raw dicts or strings
- Frontend never calls the LLM directly — always through the backend API
- `llm_client.py` is the only file that knows about OpenCode Go specifics (base URL, model names, rate limit handling) — if the API provider changes, this is the only file that should need to change
- No stage's prompt template lives outside `/backend/pipeline` — do not scatter prompts across route files or frontend

## Model Tiering (confirm exact model names before Week 1 build starts)
- Extraction: cheap/fast model — this task is close to deterministic structuring
- Decision Engine: strongest available reasoning model — this is the stage that gets judged hardest
- Redesign Generator: same tier as Decision Engine
