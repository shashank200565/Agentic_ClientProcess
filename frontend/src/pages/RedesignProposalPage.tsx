import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getRedesignProposal } from "../api/workflows";
import { WorkflowDiagram } from "../components/WorkflowDiagram";
import type { RedesignProposal } from "../types/workflow";
import { textBullets } from "../utils/workflow";
import { ScreenChat } from "../components/ScreenChat";
import { storedScreenContext } from "../utils/workflow";

export function RedesignProposalPage() {
  const { workflowId, stepId } = useParams();
  const [proposal, setProposal] = useState<RedesignProposal | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { if (workflowId && stepId) getRedesignProposal(workflowId, stepId).then(setProposal).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Generation failed.")); }, [workflowId, stepId]);
  if (error) return <p className="rounded-2xl bg-red-50 p-6 text-red-700">{error}</p>;
  if (!proposal) return <p className="rounded-3xl border border-slate-200 bg-white p-10 text-center text-slate-500">Generating agent-first redesign...</p>;
  return <><section className="mx-auto max-w-6xl"><Link to={`/review/${workflowId}`} className="text-sm font-semibold text-teal-700">← Back to step review</Link><p className="mt-8 text-sm font-semibold uppercase tracking-[0.22em] text-teal-700">03 / Redesign proposal</p><h1 className="mt-3 max-w-3xl font-display text-4xl font-semibold tracking-tight text-[#102a2c]">{proposal.current_step.name}</h1><div className="mt-8 space-y-4"><CopyCard title="Problem statement" text={proposal.problem_statement} /><CopyCard title="Proposed design" text={proposal.proposed_design} /><ListCard title="Agent responsibilities" items={proposal.agent_responsibilities} /><ListCard title="Human controls" items={proposal.human_controls} /><ListCard title="Expected benefits" items={proposal.expected_benefits} /></div><div className="mt-8"><WorkflowDiagram diagram={proposal.diagram} /></div></section><ScreenChat context={storedScreenContext(workflowId, stepId, proposal)} /></>;
}
function CopyCard({ title, text }: { title: string; text: string }) { return <article className="rounded-2xl border border-slate-200 bg-white p-6"><h2 className="font-display text-xl font-semibold text-[#102a2c]">{title}</h2><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{textBullets(text).map((item, index) => <li key={`${title}-${index}`} className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-600" />{item}</li>)}</ul></article>; }
function ListCard({ title, items }: { title: string; items: string[] }) { return <article className="rounded-2xl border border-slate-200 bg-white p-6"><h2 className="font-display text-xl font-semibold text-[#102a2c]">{title}</h2><ul className="mt-4 space-y-3">{items.map((item, index) => <li key={`${title}-${index}`} className="flex gap-3 text-sm leading-6 text-slate-600"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-600" />{item}</li>)}</ul></article>; }
