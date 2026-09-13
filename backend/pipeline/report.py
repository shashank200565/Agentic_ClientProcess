from __future__ import annotations

try:
    from backend.pipeline.schemas import ExecutiveReport, ReportMetrics, ReportStepSummary, Workflow
except ModuleNotFoundError:
    from pipeline.schemas import ExecutiveReport, ReportMetrics, ReportStepSummary, Workflow


def generate_executive_report(workflow: Workflow) -> ExecutiveReport:
    """Compile a consulting-style report from persisted analysis data only."""
    if not workflow.scores:
        raise ValueError("Workflow must be scored before a report can be generated")

    counts = {"leave_as_is": 0, "automate": 0, "redesign": 0}
    for score in workflow.scores:
        counts[score.verdict] += 1
    total = len(workflow.scores)
    average_ai = sum(item.scores.ai_suitability for item in workflow.scores) / total
    average_compliance = sum(item.scores.compliance_sensitivity for item in workflow.scores) / total
    if counts["redesign"]:
        headline = "Redesign before scaling"
    elif counts["automate"]:
        headline = "Automate selectively"
    else:
        headline = "Retain current process"

    recommendations = []
    if counts["redesign"]:
        recommendations.append(f"Prioritize {counts['redesign']} redesign step(s) with explicit human checkpoints before automation investment.")
    if counts["automate"]:
        recommendations.append(f"Implement {counts['automate']} conventional automation candidate(s) using deterministic controls and audit trails.")
    if counts["leave_as_is"]:
        recommendations.append(f"Leave {counts['leave_as_is']} step(s) unchanged where rules-based or human control is currently more appropriate.")

    step_summaries = []
    for score in workflow.scores:
        step = next((item for item in workflow.steps if item.step_id == score.step_id), None)
        if step is None:
            continue
        step_summaries.append(ReportStepSummary(
            step=step,
            score=score,
            automation_blueprint=next((item for item in workflow.automation_blueprints if item.step_id == score.step_id), None),
            redesign_proposal=next((item for item in workflow.redesign_proposals if item.step_id == score.step_id), None),
        ))

    return ExecutiveReport(
        workflow_id=workflow.workflow_id,
        workflow_name=workflow.name,
        executive_summary=(
            f"The {workflow.name} workflow contains {total} scored steps. "
            f"{counts['redesign']} step(s) warrant redesign, {counts['automate']} step(s) are conventional automation candidates, "
            f"and {counts['leave_as_is']} step(s) should remain as-is. "
            f"The portfolio-level recommendation is to {headline.lower()} while maintaining compliance controls."
        ),
        headline_verdict=headline,
        metrics=ReportMetrics(
            total_steps=total,
            leave_as_is=counts["leave_as_is"],
            automate=counts["automate"],
            redesign=counts["redesign"],
            average_ai_suitability=round(average_ai, 2),
            average_compliance_sensitivity=round(average_compliance, 2),
        ),
        key_recommendations=recommendations or ["Review the scored workflow before committing transformation budget."],
        step_summaries=step_summaries,
    )
