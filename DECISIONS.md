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

Decision: Apply this explicit post-processing rule to the four dimension scores;
the model does not choose the final verdict. Governance-action handling is checked
first so a high AI-suitability score cannot override a human control gate:

1. If `judgment_need <= 2`, `compliance_sensitivity >= 4`, and the step describes
   a sign-off, approval, escalation, or record-retention action, return `leave_as_is`.
2. Otherwise, if `repetitiveness >= 4` and `judgment_need <= 2`, return
   `leave_as_is` when `ai_suitability <= 2`, otherwise `automate`.
3. Otherwise, if `judgment_need >= 3` and `ai_suitability >= 3`, return `redesign`.
4. Otherwise, return `automate` when `ai_suitability <= 2`, otherwise `redesign`.

This is an explicit, inspectable rule and not a second LLM call.

Reason: Keeps the triage decision transparent and explainable in Q&A ("why did this get 'redesign'" should have a rule-based answer, not "the model said so").

Status: Accepted

---

## Stretch Scope

Decision: Chat Assistant (Stage 6) is cut by default. Only build if Stages 1-5 are fully working with time remaining.

Reason: Protects the core pipeline and demo reliability over feature breadth given the 3-week timeline.

Status: Accepted

---

## Orchestration Framework

Decision: Use LangGraph for verdict-conditional pipeline routing, replacing plain
function-call branching.

Reason: Mentor guidance on orchestration. The generators must exist and be independently
verified before they are wrapped into a LangGraph-coordinated flow. LangGraph also
provides the state tracking needed for workflow session resume as a side benefit.

Status: Accepted

---

## Observability Tooling

Decision: Use LangSmith for LLM call tracing across all pipeline stages instead of
building a custom logging table.

Reason: Mentor guidance on observability. LangSmith avoids building and maintaining
logging infrastructure in-house given the timeline.

Status: Accepted

---

## Automate vs. Redesign Output Distinction

Decision: `automate` and `redesign` verdicts produce different downstream outputs:
a templated Automation Blueprint versus an agentic Redesign Proposal. Both include
a static visual workflow diagram, but the generation approach is not shared.

Reason: Preserves the platform's ability to demonstrate that not every verdict
requires agentic generation.

Status: Accepted

---

## Live Editing Deferred

Decision: Chat-based conversational editing of generated redesigns or automation
blueprints, and a master routing agent for open-ended Q&A, are out of scope for this
submission.

Reason: Timeline risk. These are separate, harder systems layered on top of the core
pipeline. Static generated output is demonstrated instead, with live editing and
open-ended Q&A noted as future extensions.

Status: Accepted

Python 3.14 is fine as-is, no downgrade needed
Use raw sqlite3, not SQLModel
Frontend dev server proxies /api to localhost:8000 (no extra tooling)
Deployment deferred — local demo is the fallback plan for now
