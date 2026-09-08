import type { Workflow } from "../types/workflow";

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
