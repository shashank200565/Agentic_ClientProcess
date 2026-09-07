# Phase 0 Scoring Rubric

## Purpose

This rubric is the annotation contract for the investment-management workflow
ground-truth set. Each workflow step receives four independent scores from 1 to
5, followed by a human triage verdict. Annotators should score the step as it
operates today, not an improved or hypothetical version of the process.

The scores are ordinal labels, not percentages. Use the anchors below and write
a short evidence note when a score is not obvious from the step description.

## Scoring Dimensions

### Repetitiveness

How frequently the step repeats the same or very similar work across cases.

| Score | Anchor |
| --- | --- |
| 1 | Rare or one-off activity; the work is materially different each time. |
| 2 | Infrequent activity with some recurring elements but substantial variation. |
| 3 | Regular activity with a mixed pattern of repeatable and variable work. |
| 4 | Frequent activity that follows a mostly repeatable pattern. |
| 5 | High-volume activity with nearly identical steps, inputs, and outputs. |

### Judgment Need

How much expert interpretation, ambiguity handling, negotiation, or contextual
decision-making the step requires.

| Score | Anchor |
| --- | --- |
| 1 | Deterministic rule or lookup; little or no discretion is required. |
| 2 | Minor interpretation is needed, but clear rules resolve most cases. |
| 3 | Material judgment is needed in common exceptions or ambiguous cases. |
| 4 | Specialist judgment is needed for most cases and evidence must be weighed. |
| 5 | Highly contextual, strategic, or relationship-sensitive expert judgment is central. |

### Compliance Sensitivity

The consequence and control sensitivity of an error in this step. Consider
regulatory obligations, client mandates, fiduciary duties, auditability, and
potential financial or reputational harm.

| Score | Anchor |
| --- | --- |
| 1 | Internal convenience activity with negligible compliance consequence. |
| 2 | Low-impact control or reporting activity; errors are readily corrected. |
| 3 | Material control or client-impacting activity requiring evidence and review. |
| 4 | Regulatory, mandate, fiduciary, or audit-sensitive activity with significant consequences. |
| 5 | Critical compliance or client-protection decision where an error could cause serious breach, loss, or enforcement action. |

### AI Suitability

How suitable the step is for AI assistance or automation in a controlled
investment-management environment. Consider data availability, repeatability,
explainability, error tolerance, and the feasibility of human oversight.

| Score | Anchor |
| --- | --- |
| 1 | Poor fit: data is unavailable or the step is too bespoke, high-risk, or judgment-heavy. |
| 2 | Limited fit: AI may assist with retrieval or drafting, but reliable execution is unlikely. |
| 3 | Conditional fit: useful with constrained scope, strong controls, and mandatory human review. |
| 4 | Good fit: structured data and repeatable reasoning support controlled automation with exception handling. |
| 5 | Strong fit: deterministic, high-volume, auditable work can be automated with low residual risk. |

## Triage Verdict

The verdict is a human label in Phase 0. Do not infer it from a simple average
or silently replace it with a formula. Phase 2 will document and evaluate an
explicit rule against these labels.

| Verdict | Use when |
| --- | --- |
| `leave_as_is` | The current step is already proportionate, low-value to change, or depends on judgment that should remain human-led. |
| `automate` | The step is sufficiently repeatable and structured for controlled automation, with appropriate review and audit controls. |
| `redesign` | The step is a poor candidate for direct automation because the process, data, exceptions, or control design should change first. |

## Annotation Process

1. Each annotator scores every step independently without viewing another annotator's labels.
2. Annotators record evidence for scores that differ by more than one point or where the verdict is uncertain.
3. The team discusses disagreements and records the reconciled score and verdict in `labeled_set.json`.
4. The reconciled label is the evaluation target. Original independent labels should be retained outside the runtime dataset if they are collected.
5. Any later rubric change requires re-reviewing affected labels and recording the change in the project decisions log.

## Dataset Contract

Each step in `labeled_set.json` contains:

- `step_id`: stable identifier within the workflow.
- `name`: concise step name.
- `description`: current-state activity description.
- `scores`: the four integer rubric scores.
- `expected_verdict`: reconciled human triage label.
- `evidence`: concise rationale for the labels.

The dataset is currently marked `draft_pending_team_reconciliation` until the
team completes independent scoring and reconciliation.
