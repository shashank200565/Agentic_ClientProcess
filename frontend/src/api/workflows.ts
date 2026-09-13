import type { AutomationBlueprint, ExecutiveReport, RedesignProposal, Workflow } from "../types/workflow";

interface TextExtractionInput {
  text: string;
  name?: string;
  workflow_id?: string;
}

export async function extractWorkflow(
  input: TextExtractionInput | File,
): Promise<Workflow> {
  let response: Response;
  if (input instanceof File) {
    const form = new FormData();
    form.append("file", input);
    response = await fetch("/analyze/extract", {
      method: "POST",
      body: form,
    });
  } else {
    response = await fetch("/analyze/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
  }

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Extraction failed with status ${response.status}`);
  }
  return response.json() as Promise<Workflow>;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function scoreWorkflow(workflowId: string): Promise<Workflow> {
  return postJson<Workflow>("/analyze/score", { workflow_id: workflowId });
}

export function getAutomationBlueprint(workflowId: string, stepId: string, userNotes?: string): Promise<AutomationBlueprint> {
  return postJson<AutomationBlueprint>("/analyze/automation-blueprint", {
    workflow_id: workflowId,
    step_id: stepId,
    user_notes: userNotes || undefined,
  });
}

export function getRedesignProposal(workflowId: string, stepId: string, userNotes?: string): Promise<RedesignProposal> {
  return postJson<RedesignProposal>("/analyze/redesign", {
    workflow_id: workflowId,
    step_id: stepId,
    user_notes: userNotes || undefined,
  });
}

export async function getExecutiveReport(workflowId: string): Promise<ExecutiveReport> {
  const response = await fetch(`/reports/${workflowId}`);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Report failed with status ${response.status}`);
  }
  return response.json() as Promise<ExecutiveReport>;
}

export async function getAnalyzedWorkflows(): Promise<Workflow[]> {
  const response = await fetch("/analyze/workflows");
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Portfolio data failed with status ${response.status}`);
  }
  return response.json() as Promise<Workflow[]>;
}

export async function askScreenChat(question: string, context: Record<string, unknown>): Promise<string> {
  const response = await fetch("/analyze/screen-chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, context }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Screen assistant failed with status ${response.status}`);
  }
  const payload = await response.json() as { answer: string };
  return payload.answer;
}
