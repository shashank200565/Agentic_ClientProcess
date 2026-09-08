export type Verdict = "leave_as_is" | "automate" | "redesign";

export interface WorkflowStep {
  step_id: string;
  name: string;
  description: string;
}

export interface StepScores {
  repetitiveness: number;
  judgment_need: number;
  compliance_sensitivity: number;
  ai_suitability: number;
}

export interface StepScore {
  workflow_id: string;
  step_id: string;
  scores: StepScores;
  reasoning: string;
  verdict: Verdict;
}

export interface Workflow {
  workflow_id: string;
  name: string;
  source_type: string;
  status: "uploaded" | "extracted" | "analyzed";
  raw_text?: string | null;
  steps: WorkflowStep[];
  scores: StepScore[];
}
