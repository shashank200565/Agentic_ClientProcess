import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { scoreWorkflow } from "../api/workflows";
import { VerdictBadge } from "../components/VerdictBadge";
import type { StepScore, Workflow } from "../types/workflow";
import { riskLabel, riskScore, textBullets } from "../utils/workflow";

export function StepReviewPage() {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [error, setError] = useState("");
  const [isScoring, setIsScoring] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem("currentWorkflow");
    if (!stored || !workflowId) return;
    const extracted = JSON.parse(stored) as Workflow;
    if (extracted.workflow_id !== workflowId) return;
    setWorkflow(extracted);
    setIsScoring(true);
    scoreWorkflow(workflowId).then((scored) => {
      setWorkflow(scored);
      sessionStorage.setItem("currentWorkflow", JSON.stringify(scored));
    }).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Scoring failed.")).finally(() => setIsScoring(false));
  }, [workflowId]);

  if (!workflow || workflow.workflow_id !== workflowId) return <EmptyReview />;
  return <section className="mx-auto max-w-6xl">
    <div className="mb-10 flex flex-col justify-between gap-5 border-b border-slate-200 pb-8 sm:flex-row sm:items-end"><div><p className="mb-3 text-sm font-semibold uppercase tracking-[0.22em] text-teal-700">02 / Step review</p><h1 className="font-display text-4xl font-semibold tracking-tight text-[#102a2c]">{workflow.name}</h1><p className="mt-3 text-slate-500">{workflow.steps.length} extracted steps · scores from the Decision Engine</p></div><span className="rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-semibold text-emerald-800">{isScoring ? "Scoring..." : "Live scores"}</span></div>
    {error && <p className="mb-5 rounded-lg bg-red-50 px-3 py-2 text-xs leading-5 text-red-700">{error}</p>}
    <div className="space-y-4">{workflow.steps.map((step) => { const score = workflow.scores.find((item) => item.step_id === step.step_id); return <StepCard key={step.step_id} step={step} score={score} onGenerate={() => score?.verdict === "automate" ? navigate(`/automation/${workflow.workflow_id}/${step.step_id}`) : navigate(`/redesign/${workflow.workflow_id}/${step.step_id}`)} />; })}</div>
    <div className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-dashed border-slate-300 bg-white/60 p-5"><p className="text-sm text-slate-500">Generate a conventional blueprint or agent-first redesign for flagged steps.</p><div className="flex gap-3"><Link to={`/report/${workflow.workflow_id}`} className="rounded-lg bg-[#f2c14e] px-4 py-2 text-sm font-semibold text-[#102a2c]">View executive report</Link><Link to="/" className="rounded-lg bg-[#102a2c] px-4 py-2 text-sm font-semibold text-white">Analyze another workflow</Link></div></div>
  </section>;
}

function StepCard({ step, score, onGenerate }: { step: Workflow["steps"][number]; score?: StepScore; onGenerate: () => void }) {
  return <article className="grid gap-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_10px_35px_rgba(16,42,44,0.04)] lg:grid-cols-[minmax(0,1fr)_280px]"><div className="flex gap-4"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-[#e4eee9] font-display font-semibold text-teal-800">{String(Number(step.step_id)).padStart(2, "0")}</span><div><div className="mb-2 flex flex-wrap items-center gap-3"><h2 className="font-display text-xl font-semibold text-[#102a2c]">{step.name}</h2>{score && <VerdictBadge verdict={score.verdict} />}</div><BulletList text={step.description} /><div className="mt-4"><p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">Decision reasoning</p><BulletList text={score?.reasoning ?? "Waiting for score..."} muted /></div>{score && score.verdict !== "leave_as_is" && <button type="button" onClick={onGenerate} className="mt-5 rounded-xl bg-[#102a2c] px-4 py-2.5 text-sm font-semibold text-white">{score.verdict === "automate" ? "Generate Blueprint" : "Generate Redesign"}</button>}</div></div>{score && <div className="grid grid-cols-2 gap-2 self-start text-xs"><div className="col-span-2 rounded-xl bg-[#e4eee9] p-3"><p className="text-[10px] uppercase tracking-wide text-teal-700">Risk if unaddressed</p><p className="mt-1 font-display text-xl font-semibold text-[#102a2c]">{riskScore(score)}<span className="ml-1 text-xs font-normal text-slate-500">/5 · {riskLabel(riskScore(score))}</span></p></div>{Object.entries(score.scores).map(([key, value]) => <div key={key} className="rounded-xl bg-slate-50 p-3"><p className="mb-1 text-[10px] uppercase leading-4 tracking-wide text-slate-400">{key.replaceAll("_", " ")}</p><p className="font-display text-xl font-semibold text-[#102a2c]">{value}<span className="ml-1 text-xs font-normal text-slate-400">/5</span></p></div>)}</div>}</article>;
}

function BulletList({ text, muted = false }: { text: string; muted?: boolean }) { return <ul className={`space-y-2 text-sm leading-6 ${muted ? "text-slate-500" : "text-slate-600"}`}>{textBullets(text).map((item, index) => <li key={`${item}-${index}`} className="flex gap-2"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-600" />{item}</li>)}</ul>; }

function EmptyReview() { return <section className="mx-auto max-w-2xl rounded-3xl border border-slate-200 bg-white p-10 text-center"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-700">No workflow loaded</p><h1 className="mt-4 font-display text-3xl font-semibold text-[#102a2c]">Start with an upload</h1><Link to="/" className="mt-7 inline-flex rounded-xl bg-[#f2c14e] px-5 py-3 text-sm font-bold text-[#102a2c]">Go to upload</Link></section>; }
