import type { StepScore, Workflow } from "../types/workflow";

export function riskScore(score: StepScore): number {
  return Number((score.scores.compliance_sensitivity * 0.6 + score.scores.judgment_need * 0.4).toFixed(1));
}

export function riskLabel(value: number): "Low" | "Medium" | "High" {
  if (value >= 3.5) return "High";
  if (value >= 2.5) return "Medium";
  return "Low";
}

export function riskExplanation(score: StepScore): string {
  const label = riskLabel(riskScore(score));
  if (label === "High" && score.verdict === "leave_as_is") return "An error here could let a real compliance violation or client-protection failure go undetected, which is why this step keeps an accountable human decision-maker even where AI can help with groundwork.";
  if (label === "High" && score.verdict === "redesign") return "This step combines consequential evidence interpretation with material control exposure; an agent can organize the work, but the redesigned flow must preserve review, traceability, and an explicit human decision point.";
  if (label === "Low" && score.verdict === "automate") return "The main downside is operational inconsistency rather than expert judgment, so a deterministic automation can remove manual effort while keeping outputs auditable and easy to correct.";
  if (label === "Low" && score.verdict === "leave_as_is") return "The work is low consequence but already simple and reliable; leaving it alone avoids adding system complexity where automation would create little practical benefit.";
  return score.verdict === "automate" ? "A controlled automation is reasonable here, but exceptions should remain visible so a human can intervene when the normal path does not fit." : "The step has enough ambiguity or consequence to warrant a measured design with explicit controls rather than an unreviewed shortcut.";
}

export function textBullets(text: string): string[] {
  const parts = text
    .split(/(?:\n+|(?<=[.!?;])\s+)/)
    .map((part) => part.replace(/^[-•*]\s*/, "").trim())
    .filter(Boolean);
  if (parts.length <= 6) return parts;
  const size = Math.ceil(parts.length / 6);
  return Array.from({ length: 6 }, (_, index) => parts.slice(index * size, (index + 1) * size).join(" ")).filter(Boolean);
}

export function screenContext(workflow: Workflow, focusedStepId?: string, generated?: unknown): Record<string, unknown> {
  return {
    workflow_id: workflow.workflow_id,
    workflow_name: workflow.name,
    focused_step_id: focusedStepId,
    steps: workflow.steps.map((step) => {
      const score = workflow.scores.find((item) => item.step_id === step.step_id);
      return { ...step, score, risk_score: score ? riskScore(score) : undefined, risk_explanation: score ? riskExplanation(score) : undefined };
    }),
    automation_blueprints: workflow.automation_blueprints ?? [],
    redesign_proposals: workflow.redesign_proposals ?? [],
    focused_generated_content: generated,
  };
}

export function storedScreenContext(workflowId: string | undefined, stepId: string | undefined, generated: unknown): Record<string, unknown> {
  if (typeof window === "undefined") return { workflow_id: workflowId, focused_step_id: stepId, focused_generated_content: generated };
  const stored = sessionStorage.getItem("currentWorkflow");
  if (!stored) return { workflow_id: workflowId, focused_step_id: stepId, focused_generated_content: generated };
  try { return screenContext(JSON.parse(stored) as Workflow, stepId, generated); }
  catch { return { workflow_id: workflowId, focused_step_id: stepId, focused_generated_content: generated }; }
}
