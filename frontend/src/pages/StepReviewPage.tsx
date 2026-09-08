import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { VerdictBadge } from "../components/VerdictBadge";
import type { StepScore, Verdict, Workflow } from "../types/workflow";

const placeholderVerdicts: Verdict[] = ["automate", "automate", "redesign", "leave_as_is", "redesign"];

function placeholderScore(workflowId: string, stepId: string, index: number): StepScore {
  const verdict = placeholderVerdicts[index % placeholderVerdicts.length];
  const scores = verdict === "automate"
    ? { repetitiveness: 5, judgment_need: 1, compliance_sensitivity: 3, ai_suitability: 5 }
    : verdict === "redesign"
      ? { repetitiveness: 3, judgment_need: 4, compliance_sensitivity: 4, ai_suitability: 3 }
      : { repetitiveness: 2, judgment_need: 5, compliance_sensitivity: 5, ai_suitability: 2 };
  return { workflow_id: workflowId, step_id: stepId, scores, verdict, reasoning: "Placeholder score for frontend review. Decision Engine route is not implemented yet." };
}

export function StepReviewPage() {
  const { workflowId } = useParams();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("currentWorkflow");
    if (stored) setWorkflow(JSON.parse(stored) as Workflow);
  }, []);

  if (!workflow || workflow.workflow_id !== workflowId) {
    return <EmptyReview />;
  }

  return (
    <section className="mx-auto max-w-6xl">
      <div className="mb-10 flex flex-col justify-between gap-5 border-b border-slate-200 pb-8 sm:flex-row sm:items-end">
        <div><p className="mb-3 text-sm font-semibold uppercase tracking-[0.22em] text-teal-700">02 / Step review</p><h1 className="font-display text-4xl font-semibold tracking-tight text-[#102a2c]">{workflow.name}</h1><p className="mt-3 text-slate-500">{workflow.steps.length} extracted steps · scores below are frontend placeholders</p></div>
        <span className="rounded-full bg-amber-100 px-3 py-1.5 text-xs font-semibold text-amber-800 ring-1 ring-amber-200">Decision Engine placeholder</span>
      </div>
      <div className="space-y-4">
        {workflow.steps.map((step, index) => {
          const score = placeholderScore(workflow.workflow_id, step.step_id, index);
          return <article key={step.step_id} className="grid gap-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_10px_35px_rgba(16,42,44,0.04)] lg:grid-cols-[minmax(0,1fr)_280px]">
            <div className="flex gap-4"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-[#e4eee9] font-display font-semibold text-teal-800">{String(index + 1).padStart(2, "0")}</span><div><div className="mb-2 flex flex-wrap items-center gap-3"><h2 className="font-display text-xl font-semibold text-[#102a2c]">{step.name}</h2><VerdictBadge verdict={score.verdict} /></div><p className="max-w-2xl text-sm leading-6 text-slate-600">{step.description}</p><p className="mt-4 text-xs leading-5 text-slate-400">{score.reasoning}</p></div></div>
            <div className="grid grid-cols-2 gap-2 self-start text-xs">{Object.entries(score.scores).map(([key, value]) => <div key={key} className="rounded-xl bg-slate-50 p-3"><p className="mb-1 text-[10px] uppercase leading-4 tracking-wide text-slate-400">{key.replaceAll("_", " ")}</p><p className="font-display text-xl font-semibold text-[#102a2c]">{value}<span className="ml-1 text-xs font-normal text-slate-400">/5</span></p></div>)}</div>
          </article>;
        })}
      </div>
      <div className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-dashed border-slate-300 bg-white/60 p-5"><p className="text-sm text-slate-500">Real scoring will replace these values when `/analyze/score` is implemented.</p><Link to="/" className="rounded-lg bg-[#102a2c] px-4 py-2 text-sm font-semibold text-white">Analyze another workflow</Link></div>
    </section>
  );
}

function EmptyReview() {
  return <section className="mx-auto max-w-2xl rounded-3xl border border-slate-200 bg-white p-10 text-center"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-700">No workflow loaded</p><h1 className="mt-4 font-display text-3xl font-semibold text-[#102a2c]">Start with an upload</h1><p className="mt-3 text-slate-500">This review page reads the latest extraction from the current browser session.</p><Link to="/" className="mt-7 inline-flex rounded-xl bg-[#f2c14e] px-5 py-3 text-sm font-bold text-[#102a2c]">Go to upload</Link></section>;
}
