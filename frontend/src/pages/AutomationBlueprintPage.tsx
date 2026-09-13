import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getAutomationBlueprint } from "../api/workflows";
import { WorkflowDiagram } from "../components/WorkflowDiagram";
import type { AutomationBlueprint } from "../types/workflow";

export function AutomationBlueprintPage() {
  const { workflowId, stepId } = useParams();
  const [blueprint, setBlueprint] = useState<AutomationBlueprint | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { if (workflowId && stepId) getAutomationBlueprint(workflowId, stepId).then(setBlueprint).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Generation failed.")); }, [workflowId, stepId]);
  if (error) return <ErrorState message={error} />;
  if (!blueprint) return <LoadingState label="Generating conventional blueprint..." />;
  return <section className="mx-auto max-w-6xl"><Link to={`/review/${workflowId}`} className="text-sm font-semibold text-teal-700">← Back to step review</Link><p className="mt-8 text-sm font-semibold uppercase tracking-[0.22em] text-teal-700">03 / Automation blueprint</p><h1 className="mt-3 max-w-3xl font-display text-4xl font-semibold tracking-tight text-[#102a2c]">{blueprint.current_step.name}</h1><p className="mt-3 text-slate-500">A constrained, conventional path for a step judged suitable for automation.</p><div className="mt-8 grid gap-4 sm:grid-cols-3"><Info label="Mechanism" value={blueprint.mechanism_type.replaceAll("_", " ")} /><Info label="Trigger" value={blueprint.trigger_condition} /><Info label="Rationale" value={blueprint.rationale} /></div><div className="mt-8"><WorkflowDiagram diagram={blueprint.diagram} /></div></section>;
}

function Info({ label, value }: { label: string; value: string }) { return <div className="rounded-2xl border border-slate-200 bg-white p-5"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{label}</p><p className="mt-3 text-sm leading-6 text-slate-700">{value}</p></div>; }
function LoadingState({ label }: { label: string }) { return <section className="rounded-3xl border border-slate-200 bg-white p-10 text-center text-slate-500">{label}</section>; }
function ErrorState({ message }: { message: string }) { return <section className="rounded-3xl border border-red-200 bg-red-50 p-10 text-center text-red-700">{message}</section>; }
