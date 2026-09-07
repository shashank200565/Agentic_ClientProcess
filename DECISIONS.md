# Architecture & Product Decisions

## Domain Scope

Decision: Focus v1 entirely on investment management workflows (mandate breach investigation, exposure monitoring, client onboarding, performance reporting, trade confirmation matching). No cross-industry examples in the demo set.

Reason: Mentor guidance — depth in one domain is more credible to judges than shallow breadth across banking/healthcare/manufacturing.

Status: Accepted

---

## Build Platform

Decision: Custom web application (React + FastAPI), not a no-code platform (Bubble/node-canvas builder rejected).

Reason: No-code platforms make the eval-iteration loop for the Decision Engine slower and harder to debug; team needs tight control over prompt iteration against the labeled ground-truth set. Full engineering control was judged more valuable than build speed given the team has agentic coding assistance.

Status: Accepted

---

## LLM Provider

Decision: OpenCode Go subscription as the sole API provider, used across all pipeline stages via `llm_client.py`, with different model tiers per stage rather than separate subscriptions.

Reason: Only available paid access. One key, multiple prompt templates — no architectural requirement for multiple providers, since "agent" = distinct prompt, not distinct API key.

Status: Accepted

Follow-up: Confirm and lock exact model names for Extraction vs. Decision Engine before Phase 1 build starts, and re-confirm before final demo run (do not let the demo run on a rate-limit-rotated model different from what was eval-tested).

---

## Methodology

Decision: Eval-first. Build the labeled ground-truth set (15-20 workflows, hand-scored) before writing Decision Engine scoring logic.

Reason: Makes the headline accuracy claim measurable and defensible instead of asserted. This is the team's core differentiation argument for judges.

Status: Accepted

---

## Verdict Logic

Decision: [TO BE FILLED once Phase 2 is underway] — the rule combining the four dimension scores (repetitiveness, judgment, compliance, AI-suitability) into a final leave-as-is/automate/redesign verdict should be an explicit, inspectable rule — not a second LLM call.

Reason: Keeps the triage decision transparent and explainable in Q&A ("why did this get 'redesign'" should have a rule-based answer, not "the model said so").

Status: Pending — finalize during Phase 2 and update this entry.

---

## Stretch Scope

Decision: Chat Assistant (Stage 6) is cut by default. Only build if Stages 1-5 are fully working with time remaining.

Reason: Protects the core pipeline and demo reliability over feature breadth given the 3-week timeline.

Status: Accepted

Python 3.14 is fine as-is, no downgrade needed
Use raw sqlite3, not SQLModel
Frontend dev server proxies /api to localhost:8000 (no extra tooling)
Deployment deferred — local demo is the fallback plan for now
