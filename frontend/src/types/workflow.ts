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
  automation_blueprints?: AutomationBlueprint[];
  redesign_proposals?: RedesignProposal[];
}

export interface DiagramNode {
  id: string;
  label: string;
  node_type: string;
}

export interface DiagramEdge {
  source: string;
  target: string;
  label?: string | null;
}

export interface StaticWorkflowDiagram {
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

export interface AutomationBlueprint {
  workflow_id: string;
  step_id: string;
  current_step: WorkflowStep;
  mechanism_type: "rules_engine" | "rpa" | "scheduled_job" | "existing_stp_extension";
  trigger_condition: string;
  rationale: string;
  diagram: StaticWorkflowDiagram;
}

export interface RedesignProposal {
  workflow_id: string;
  step_id: string;
  current_step: WorkflowStep;
  problem_statement: string;
  proposed_design: string;
  agent_responsibilities: string[];
  human_controls: string[];
  expected_benefits: string[];
  diagram: StaticWorkflowDiagram;
}

export interface ReportMetrics {
  total_steps: number;
  leave_as_is: number;
  automate: number;
  redesign: number;
  average_ai_suitability: number;
  average_compliance_sensitivity: number;
}

export interface ReportStepSummary {
  step: WorkflowStep;
  score: StepScore;
  automation_blueprint?: AutomationBlueprint | null;
  redesign_proposal?: RedesignProposal | null;
}

export interface ExecutiveReport {
  workflow_id: string;
  workflow_name: string;
  executive_summary: string;
  headline_verdict: string;
  metrics: ReportMetrics;
  key_recommendations: string[];
  step_summaries: ReportStepSummary[];
}

export interface WorkflowSession {
  session_id: string;
  workflow_id: string;
  current_stage: string;
  completed_step_ids: string[];
  workflow: Workflow;
}
