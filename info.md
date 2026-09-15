# Agentic Workflow Diagnostic & Redesign Platform

## 1. Project Summary

This project is an investment-management workflow diagnostic platform.

A user uploads an SOP PDF or pastes workflow text. The system:

1. Extracts the workflow into ordered structured steps.
2. Scores every step across four dimensions.
3. Produces a triage verdict:
   - `leave_as_is`
   - `automate`
   - `redesign`
4. Displays the scores, reasoning, and verdict in a React frontend.
5. Evaluates the Decision Engine against a manually labeled ground-truth set.

The goal is to avoid blindly applying AI to broken, deterministic, or highly regulated processes. The system first determines whether a step should remain unchanged, be conventionally automated, or be redesigned around an AI agent.

## 2. End-to-End Flow

```text
PDF upload
   |
   v
React/Vite frontend
   |
   v
POST /analyze/extract
   |
   v
PDF text extraction with pypdf
   |
   v
Extraction LLM: GLM-5.3-Flash
   |
   v
Pydantic WorkflowStep[]
   |
   v
SQLite persistence
   |
   v
POST /analyze/score
   |
   v
Decision Engine: GPT 5.6 Luna
   |
   v
Pydantic StepScore[]
   |
   v
Rule-based verdict calculation
   |
   v
Frontend step review page
```

The frontend never calls the LLM directly. All model calls go through FastAPI.

## 3. Technology Stack

### Backend

- Python 3.14 in the current local environment
- FastAPI
- Uvicorn
- Pydantic v2
- SQLite using Python's built-in `sqlite3`
- `pypdf` for PDF text extraction
- `pdfplumber` dependency for PDF processing
- OpenCode Go API for LLM access

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Recharts dependency for future dashboards

### LLM Models

| Stage | Model |
| --- | --- |
| Extraction | GLM-5.3-Flash |
| Decision Engine | GPT 5.6 Luna |

The extraction model is cheaper and faster. The Decision Engine uses a stronger reasoning model because its output is evaluated against human labels.

## 4. Backend Architecture

### FastAPI Application

Main file:

```text
backend/api/main.py
```

Responsibilities:

- Creates the FastAPI application.
- Registers API routers.
- Exposes `/health`.

Current routes:

```text
GET  /health
POST /analyze/extract
POST /analyze/score
```

### Extraction Route

File:

```text
backend/api/routes/analysis.py
```

`POST /analyze/extract` accepts a PDF upload, text upload, or JSON text input. It extracts document text, calls the extraction pipeline, creates a `Workflow` Pydantic model, saves it to SQLite, and returns the structured workflow.

### Scoring Route

`POST /analyze/score` receives:

```json
{
  "workflow_id": "workflow-id"
}
```

It loads the workflow, scores every step, applies the deterministic verdict rule, persists the analyzed workflow, and returns the complete result.

## 5. Pydantic Data Models

File:

```text
backend/pipeline/schemas.py
```

### Workflow

Represents the complete workflow:

```text
workflow_id
name
source_type
status
raw_text
steps
scores
```

Possible statuses:

```text
uploaded
extracted
analyzed
```

### WorkflowStep

Represents one extracted process step:

```text
step_id
name
description
```

### StepScores

Contains four integer scores from 1 to 5:

```text
repetitiveness
judgment_need
compliance_sensitivity
ai_suitability
```

### StepScore

Represents the Decision Engine result:

```text
workflow_id
step_id
scores
reasoning
verdict
```

Pydantic validates LLM responses before they enter the application or database.

## 6. LLM Client

File:

```text
backend/pipeline/llm_client.py
```

This is the only file that knows how to communicate with OpenCode Go.

Responsibilities:

- Loads environment variables.
- Selects extraction or reasoning models.
- Maps model names to provider IDs.
- Selects the correct provider protocol.
- Calls `/responses` or `/chat/completions`.
- Requests JSON output.
- Parses the structured response.
- Validates the response with Pydantic.
- Raises `LLMClientError` on failures.

Environment configuration is based on `.env.example`:

```env
OPENCODE_GO_API_KEY=your_key_here
OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1
OPENCODE_GO_EXTRACTION_MODEL=GLM-5.3-Flash
OPENCODE_GO_REASONING_MODEL=GPT 5.6 Luna
DATABASE_PATH=backend/data/app.db
```

## 7. Extraction Pipeline

File:

```text
backend/pipeline/extraction.py
```

The extraction prompt instructs the model to:

- Extract current-state investment-management workflows.
- Preserve the actual sequence.
- Split materially different activities.
- Avoid inventing systems or approvals.
- Return structured JSON.
- Provide a concise name and description for each step.

The result is validated as an `ExtractedSteps` model containing `WorkflowStep[]`.

### Extraction Granularity Correction

The quarterly performance-report SOP originally produced 12 extracted steps while the fixed labeled set contained 11. The extractor split:

```text
Establish reporting period and data sources
Retrieve portfolio and benchmark data
```

These were merged into the labeled step:

```text
Data source identification
```

The labeled set remains the fixed reference. Extraction output was corrected rather than changing the ground truth.

## 8. Decision Engine

File:

```text
backend/pipeline/decision_engine.py
```

The Decision Engine scores each step independently and returns reasoning tied to the step description and workflow context.

### Scoring Dimensions

#### Repetitiveness

How frequently the same or similar work repeats.

| Score | Meaning |
| ---: | --- |
| 1 | Rare or one-off activity |
| 2 | Infrequent with substantial variation |
| 3 | Regular mixed pattern |
| 4 | Frequent and mostly repeatable |
| 5 | High-volume and nearly identical |

#### Judgment Need

How much interpretation, ambiguity handling, or contextual decision-making is required.

| Score | Meaning |
| ---: | --- |
| 1 | Deterministic rule or lookup |
| 2 | Minor interpretation |
| 3 | Material judgment in exceptions |
| 4 | Specialist judgment for most cases |
| 5 | Highly contextual expert judgment |

#### Compliance Sensitivity

The consequence and control sensitivity of an error.

| Score | Meaning |
| ---: | --- |
| 1 | Negligible compliance consequence |
| 2 | Low-impact control or reporting activity |
| 3 | Material control or client-impacting activity |
| 4 | Regulatory, mandate, fiduciary, or audit-sensitive |
| 5 | Critical client-protection or compliance decision |

#### AI Suitability

How much AI reasoning can improve the step beyond deterministic automation.

| Score | Meaning |
| ---: | --- |
| 1 | Poor fit |
| 2 | Limited fit |
| 3 | Conditional fit with controls |
| 4 | Good fit for controlled automation |
| 5 | Strong fit for auditable automation |

High AI suitability does not imply full autonomy. Human approval may still be required.

### Calibration Principles

Procedural steps should normally receive low judgment and compliance scores:

- Checking whether data is available.
- Comparing values against a fixed threshold.
- Flagging anomalies against defined rules.
- Loading a portfolio snapshot.
- Calculating exposure percentages.
- Creating standardized exception records.
- Placing approved content into a standard template.

The fact that a step feeds a compliance process does not automatically make the step itself highly judgment-heavy or highly compliance-sensitive.

Interpretive steps should normally receive higher scores:

- Determining root cause.
- Resolving conflicting records.
- Deciding whether an exception is a genuine breach.
- Interpreting ambiguous mandate language.
- Selecting a conclusion for human approval.
- Drafting contextual explanations from multiple evidence sources.

## 9. Rule-Based Verdict Logic

The model does not directly choose the final verdict. The model provides four scores and reasoning; the backend applies an explicit rule.

```text
1. If judgment_need <= 2, compliance_sensitivity >= 4,
   and the step describes sign-off, approval, escalation,
   or record retention:
       leave_as_is

2. If repetitiveness >= 4 and judgment_need <= 2:
       ai_suitability <= 2 -> leave_as_is
       otherwise -> automate

3. If judgment_need >= 3 and ai_suitability >= 3:
       redesign

4. Otherwise:
       ai_suitability <= 2 -> automate
       otherwise -> redesign
```

This makes the verdict explainable, deterministic, and reproducible.

## 10. Automate Versus Redesign

### `automate`

Used when:

- The process is structured.
- Inputs are predictable.
- Rules are clear.
- Traditional automation is sufficient.

Possible outputs include rules engines, scheduled jobs, and RPA.

### `redesign`

Used when:

- The process involves ambiguity.
- Evidence must be synthesized.
- The current workflow needs to change.
- Human-in-the-loop agentic reasoning is appropriate.

The project does not treat every step as an AI-agent opportunity.

## 11. Database

Files:

```text
backend/db/schema.sql
backend/db/db.py
```

Main tables:

```text
workflows
workflow_steps
step_scores
redesign_proposals
```

The database stores the original workflow text, extracted steps, score dimensions, reasoning, verdicts, and workflow status.

SQLite was selected because the application is currently a single-user local/demo application with a small structured dataset.

## 12. Frontend Architecture

Important files:

```text
frontend/src/App.tsx
frontend/src/pages/UploadPage.tsx
frontend/src/pages/StepReviewPage.tsx
frontend/src/api/workflows.ts
frontend/src/types/workflow.ts
frontend/vite.config.ts
```

### Upload Flow

1. User selects a PDF or enters text.
2. Frontend calls `/analyze/extract`.
3. Frontend receives the workflow ID.
4. Frontend calls `/analyze/score`.
5. Frontend stores the analyzed workflow in `sessionStorage`.
6. Frontend navigates to the review page.

### Step Review Page

The review page displays:

- Step name
- Step description
- Verdict badge
- Model reasoning
- Repetitiveness score
- Judgment need score
- Compliance sensitivity score
- AI suitability score

The frontend now uses real `workflow.scores` returned by the backend. It no longer generates placeholder scores.

### Vite Proxy

During development:

```text
/analyze -> http://127.0.0.1:8000
/health  -> http://127.0.0.1:8000
```

This avoids local CORS issues.

## 13. Evaluation Methodology

Files:

```text
eval/rubric.md
```

The fixed ground-truth set contains five investment-management workflows:

1. Trade confirmation matching
2. Passive exposure limit checking
3. Mandate breach investigation
4. Client onboarding suitability review
5. Quarterly performance reporting

The finalized set contains 44 labeled steps.

### Metrics

#### Exact Agreement

The model score equals the labeled score exactly.

#### Within-1 Agreement

The model score differs from the labeled score by no more than one point.

#### Verdict Agreement

The model-generated final verdict exactly matches the labeled verdict.

#### Mean Absolute Error

Average absolute difference between model and labeled scores per dimension.

## 14. Evaluation Results

After AI-suitability calibration and quarterly extraction correction, the saved v2 evaluation reported:

```text
Overall verdict agreement: 37/44 = 84.09%
```

Overall dimension agreement:

| Dimension | Exact | Within 1 |
| --- | ---: | ---: |
| Repetitiveness | 36.36% | 81.82% |
| Judgment need | 47.73% | 90.91% |
| Compliance sensitivity | 45.45% | 88.64% |
| AI suitability | 20.45% | 93.18% |

The latest targeted quarterly judgment/compliance calibration produced:

```text
Verdict agreement: 8/11 = 72.73%
Judgment need exact: 9/11 = 81.82%
Judgment need within-1: 11/11 = 100%
Compliance exact: 4/11 = 36.36%
Compliance within-1: 10/11 = 90.91%
```

The judgment calibration improved agreement substantially. Remaining quarterly verdict mismatches are mainly caused by AI-suitability outputs and the deterministic verdict rule.

## 15. Important Repository Files

### Product and Architecture

```text
PROJECT.md
ARCHITECTURE.md
TASKS.md
PROGRESS.md
DECISIONS.md
README.md
```

### Backend

```text
backend/api/main.py
backend/api/routes/analysis.py
backend/pipeline/schemas.py
backend/pipeline/llm_client.py
backend/pipeline/extraction.py
backend/pipeline/decision_engine.py
backend/db/schema.sql
backend/db/db.py
```

### Frontend

```text
frontend/src/App.tsx
frontend/src/pages/UploadPage.tsx
frontend/src/pages/StepReviewPage.tsx
frontend/src/api/workflows.ts
frontend/src/types/workflow.ts
frontend/vite.config.ts
frontend/package.json
```

### Evaluation

```text
eval/rubric.md
eval/labeled_set.json
eval/run_eval.py
eval/decision_engine_v1_report.json
eval/decision_engine_v2_report.json
eval/decision_engine_v2_predictions.json
eval/decision_engine_v2_quarterly_corrected_predictions.json
eval/decision_engine_quarterly_judgment_compliance_calibration.json
```

## 16. Completed Work

- Product definition and investment-management domain scope.
- Five SOP demo documents.
- Ground-truth labeled set.
- Scoring rubric.
- PDF/text extraction.
- FastAPI backend.
- SQLite persistence.
- OpenCode Go LLM integration.
- Structured Pydantic schemas.
- Decision Engine.
- Deterministic verdict logic.
- Evaluation harness.
- Prompt calibration.
- Real frontend upload flow.
- Real frontend scoring flow.
- Real step review page.
- Automation Blueprint Generator with persisted structured output and diagrams.
- Redesign Generator with persisted structured output, diagram normalization, and human-control fields.
- LangGraph verdict-conditional orchestration.
- LangSmith tracing hooks for pipeline LLM calls.
- Portfolio dashboard with Recharts visualizations and workflow risk summaries.
- Executive report generation and print-to-PDF view.
- Workflow session persistence and resume API.
- Grounded screen assistant with persisted workflow context.
- Determinism investigations for extraction and scoring across the five demo workflows.
- Explicit extraction `temperature=0.0` and narrow judgment/AI boundary averaging with median-of-3 calls.
- Final demo pipeline run with generated outputs persisted for all flagged steps.
- Blue fintech visual system across the frontend, horizontal React Flow diagrams, reduced-density generator pages, and removal of the Resume Session UI route.

## 17. Not Yet Complete

- Deployment.
- Final frozen extraction snapshot is saved at `eval/final_extraction_snapshot.json` with 7/6/10/10/11 steps across the five demo PDFs.
- `eval/labeled_set.json` descriptions are aligned word-for-word to that snapshot. The final aligned current-pipeline evaluation is 81.82% verdict agreement (36/44).
- Do not re-extract the five demo PDFs again; the snapshot is the permanent evaluation reference.
- The Chat Assistant remains a scoped screen assistant; open-ended master routing is intentionally deferred.

## 18. Interview Questions and Answers

### Why use an LLM here?

Workflow steps contain natural-language descriptions, ambiguity, and context. The LLM interprets the work, while the final verdict remains deterministic and inspectable.

### Why not let the LLM choose the verdict?

A pure LLM verdict is difficult to audit and reproduce. The system separates model-based scoring from application-level verdict logic.

### Why use two models?

Extraction is mostly structured information extraction, so it uses a cheaper model. Decision scoring requires stronger reasoning and calibration, so it uses GPT 5.6 Luna.

### Why use Pydantic?

Pydantic validates every stage boundary and prevents malformed LLM responses from propagating through the system.

### Why SQLite?

The current application is a single-user local/demo application with a small structured dataset. SQLite minimizes operational complexity.

### Why not use AI for every step?

Some work is better handled by deterministic rules. The platform distinguishes human-led work, conventional automation, and agentic redesign.

### How is the system evaluated?

It is evaluated against a manually reconciled labeled set using exact agreement, within-one agreement, mean absolute error, and verdict agreement.

### What happens when extraction produces the wrong number of steps?

The labeled set is the fixed reference. Extraction granularity is corrected to match the established ground truth rather than changing the labels to match the model.

### How does the frontend connect to the backend?

The frontend calls `/analyze/extract` and `/analyze/score`. It never calls the LLM provider directly. Vite proxies those requests to FastAPI during development.

## 19. Demo Explanation

> I upload an investment-management SOP. The extraction stage converts the document into structured workflow steps using GLM-5.3-Flash. Those steps are stored in SQLite and passed to the Decision Engine. GPT 5.6 Luna scores each step on repetitiveness, judgment need, compliance sensitivity, and AI suitability. The model also provides evidence-based reasoning. The final triage verdict is not directly generated by the model; it is calculated by a deterministic rule in the backend. This gives us transparent and reproducible recommendations. The frontend then displays the real scores and reasoning returned by the backend.

The project is not only an LLM wrapper. It combines structured extraction, schema validation, calibrated reasoning, deterministic decision logic, database persistence, frontend visualization, and measurable evaluation against human ground truth.

## 20. Running the Project

### Backend

```powershell
cd E:\capstone\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --reload
```

### Frontend

```powershell
cd E:\capstone\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Backend health check:

```text
http://127.0.0.1:8000/health
```
