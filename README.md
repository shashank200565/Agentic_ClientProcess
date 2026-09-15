# Agentic Workflow Diagnostic & Redesign Platform

Team Mastikhors — Deloitte Capstone Programme 2026

The platform helps investment-management transformation teams decide whether a workflow should be left as-is, conventionally automated, or redesigned around bounded AI agents.

## Current Product

The working demo supports:

- Uploading investment-management SOP PDFs or pasted workflow text.
- Structured workflow extraction with Pydantic validation.
- Per-step scoring for repetitiveness, judgment need, compliance sensitivity, and AI suitability.
- Deterministic triage verdicts: `leave_as_is`, `automate`, or `redesign`.
- Conventional automation blueprints for automate verdicts.
- Agent-first redesign proposals with human controls for redesign verdicts.
- LangGraph verdict-conditional orchestration.
- Persisted SQLite workflow and generated-output state.
- Portfolio dashboard with risk summaries and Recharts visualizations.
- Executive report view with print-to-PDF support.
- Grounded screen assistant for explaining stored workflow analysis.

The five investment-management demo workflows are trade confirmation matching, passive exposure limit checking, mandate breach investigation, client onboarding suitability review, and quarterly performance report generation.

## Tech Stack

- Backend: Python 3.12, FastAPI, Pydantic v2, Uvicorn, SQLite.
- Pipeline: OpenCode Go-compatible LLM endpoint, LangGraph, LangSmith, pypdf/pdfplumber.
- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, React Flow, Dagre.
- LLM model tiers: GLM-5.3-Flash for extraction and GPT 5.6 Luna for reasoning/scoring and redesign generation.

## Setup

### Backend

```powershell
cd E:\capstone\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

The backend expects `OPENCODE_GO_API_KEY` in `backend/.env`. See `.env.example` for the supported configuration.

### Frontend

```powershell
cd E:\capstone\frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/analyze`, `/reports`, `/sessions`, and `/health` to the FastAPI backend at `http://127.0.0.1:8000`.

## Main Routes

- `/` — upload and extract/score a workflow.
- `/review/:workflowId` — focused step-by-step scoring review and horizontal workflow map.
- `/automation/:workflowId/:stepId` — automation blueprint.
- `/redesign/:workflowId/:stepId` — agent-first redesign proposal.
- `/redesigned-flow/:workflowId` — generated outputs across a workflow.
- `/report/:workflowId` — executive report.
- `/dashboard` — portfolio view.

Resume-session persistence remains available in the backend API, but the Resume Session frontend page was removed from the current UI flow.

## Evaluation

The evaluation set contains 44 labeled steps across the five demo workflows. Evaluation reports exact score agreement, within-one agreement, mean absolute error, and verdict agreement using `eval/run_eval.py`.

Historical v3 agreement was 86.36% (38/44 verdicts). A later rerun against a different live extraction/scoring snapshot produced 79.55%, showing why extraction output and scoring predictions must be frozen together for a comparable final metric.

The final frozen extraction snapshot is `eval/final_extraction_snapshot.json`. It contains the exact outputs of the final extraction pass for all five PDFs, with 7/6/10/10/11 steps. `eval/labeled_set.json` now carries the matching descriptions word-for-word. The aligned final evaluation produced **81.82% verdict agreement (36/44)**. Do not re-extract the demo PDFs without deliberately creating a new evaluation snapshot.

## Documentation

- [Project scope](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Tasks](TASKS.md)
- [Progress](PROGRESS.md)
- [Decisions](DECISIONS.md)
- [Evaluation history](eval/README.md)
- [AI coding instructions](AGENTS.md)
