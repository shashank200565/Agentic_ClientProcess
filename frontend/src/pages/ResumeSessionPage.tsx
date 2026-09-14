import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getWorkflowSessions } from "../api/workflows";
import type { WorkflowSession } from "../types/workflow";

export function ResumeSessionPage() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<WorkflowSession[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { getWorkflowSessions().then(setSessions).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Session list failed.")); }, []);
  const continueTo = (session: WorkflowSession) => { sessionStorage.setItem("currentWorkflow", JSON.stringify(session.workflow)); navigate(session.current_stage === "uploaded" ? "/" : `/review/${session.workflow_id}`); };
  return <section className="mx-auto max-w-5xl"><div className="mb-10 border-b border-slate-200 pb-8"><p className="text-sm font-semibold uppercase tracking-[0.22em] text-teal-700">04 / Resume session</p><h1 className="mt-3 font-display text-4xl font-semibold tracking-tight text-[#102a2c]">Pick up exactly where the work paused.</h1><p className="mt-3 text-slate-500">Recent workflow sessions are loaded from the backend so you can continue without repeating analysis.</p></div>{error && <p className="mb-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}{!error && sessions.length === 0 && <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">No saved workflow sessions yet.</div>}<div className="space-y-4">{sessions.map((session) => <article key={session.session_id} className="flex flex-col justify-between gap-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_8px_25px_rgba(16,42,44,0.04)] sm:flex-row sm:items-center"><div><h2 className="font-display text-xl font-semibold text-[#102a2c]">{session.workflow.name}</h2><div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold"><span className="rounded-full bg-teal-100 px-2.5 py-1 text-teal-800">Stage: {session.current_stage}</span><span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">{session.completed_step_ids.length} completed steps</span></div></div><button type="button" onClick={() => continueTo(session)} className="rounded-xl bg-[#102a2c] px-5 py-2.5 text-sm font-semibold text-white">Continue →</button></article>)}</div><Link to="/" className="mt-8 inline-flex text-sm font-semibold text-teal-700">Start a new workflow</Link></section>;
}
