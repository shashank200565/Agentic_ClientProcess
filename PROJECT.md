# Project

## Name
Agentic Workflow Diagnostic & Redesign Platform (Team Mastikhors)

## Problem
Enterprises can't reliably tell whether a workflow should be left as-is, conventionally automated, or redesigned around AI agents. This judgment currently exists only as tacit consultant expertise, not a repeatable, measurable process. Teams waste agentic AI budget automating workflows that were already broken instead of fixing the underlying design.

## Domain Focus (v1)
Investment management. All example/demo workflows come from this domain (mandate breach investigation, exposure monitoring, client onboarding suitability review, performance reporting, trade confirmation matching). Do not build generic cross-industry examples for v1 — depth in one domain over breadth.

## Goal
Given a workflow (as document upload or step list), the platform scores each step and returns a triage verdict — leave as-is / automate / redesign — with transparent reasoning, and rolls this up into a portfolio view and a client-ready report.

## Users
Transformation/consulting teams assessing which of a client's workflows are worth agentic investment, before committing engineering budget.

## Core Features (in priority order — do not reorder without updating this file)
1. Extraction Agent — raw document/transcript → structured step list
2. Analysis & Decision Engine — per-step scoring (repetitiveness, judgment need, compliance sensitivity, AI-suitability) + reasoning + verdict
3. Automation Blueprint Generator — templated conventional automation proposal for "automate" verdict steps
4. Redesign Generator — agent-first redesign proposal for "redesign" verdict steps
5. Portfolio Dashboard — complexity/exception grid across all analyzed workflows
6. Executive Report — auto-generated consulting-style summary
7. Chat Assistant (STRETCH — build only if 1-6 are done and stable; open-ended master routing/Q&A remains deferred)

## Non-Goals (v1)
- No live enterprise system integration (no ERP/CRM connectors)
- No proprietary model training or fine-tuning
- No multi-tenant auth/user management — single demo user is fine
- No node-based visual workflow builder in the UI
- No support for industries beyond investment management in the demo set
- No live conversational workflow editing of generated automation or redesign output in v1; this is a deferred future extension, not a rejected idea.
- No master routing agent for open-ended Q&A in v1; this is a deferred future extension, not a rejected idea.

## Constraints
- Must be a real web application (not a no-code platform)
- 3-person team + coding agents, ~3-week timeline, hard deadline Sept 16, 2026
- Single API provider available: OpenCode Go subscription (rate-limited, dollar-metered per 5hr/week/month)
- Headline KPI is measurable: Decision Engine agreement % against a hand-labeled ground-truth set — this must be real, not asserted
- Every pipeline stage must output structured, schema-validated data (Pydantic) — no free-text parsing between stages

## Success Criteria for Submission
- Working end-to-end demo: upload/select an investment-management workflow → see extraction → see per-step scores + reasoning → see redesign for flagged steps → see it on the dashboard → generate report
- A real, reported agreement score between Decision Engine output and the team's hand-labeled ground truth (15-20 workflows)
- At least one workflow demo that shows step-level *variance* in verdicts (not everything scored the same)
