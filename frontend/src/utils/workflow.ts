import type { StepScore } from "../types/workflow";

export function riskScore(score: StepScore): number {
  return Number((score.scores.compliance_sensitivity * 0.6 + score.scores.judgment_need * 0.4).toFixed(1));
}

export function riskLabel(value: number): "Low" | "Medium" | "High" {
  if (value >= 3.5) return "High";
  if (value >= 2.5) return "Medium";
  return "Low";
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
