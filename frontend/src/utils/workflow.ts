import type { StepScore } from "../types/workflow";

export function riskScore(score: StepScore): number {
  return Number((score.scores.compliance_sensitivity * 0.6 + score.scores.judgment_need * 0.4).toFixed(1));
}

export function riskLabel(value: number): "Low" | "Medium" | "High" {
  if (value >= 3.5) return "High";
  if (value >= 2.5) return "Medium";
  return "Low";
}

export function riskExplanation(score: StepScore): string {
  const { repetitiveness, judgment_need, compliance_sensitivity, ai_suitability } = score.scores;
  const label = riskLabel(riskScore(score));
  if (label === "High") {
    if (score.verdict === "leave_as_is") return `High risk: significant compliance exposure (${compliance_sensitivity}/5) and professional judgment (${judgment_need}/5) make this a high-stakes step; leave_as_is preserves accountable human control.`;
    return `High risk: significant compliance exposure (${compliance_sensitivity}/5) and professional judgment (${judgment_need}/5) require strong controls before pursuing the ${score.verdict} path.`;
  }
  if (label === "Low") return `Low risk: this step is highly repetitive (${repetitiveness}/5), has limited professional judgment (${judgment_need}/5), and carries modest compliance exposure (${compliance_sensitivity}/5); its AI suitability is ${ai_suitability}/5.`;
  return `Medium risk: compliance exposure is ${compliance_sensitivity}/5 and professional judgment is ${judgment_need}/5; the ${score.verdict.replaceAll("_", " ")} verdict balances control with a measured next step.`;
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
