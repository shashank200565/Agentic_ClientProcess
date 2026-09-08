import type { Verdict } from "../types/workflow";

const labels: Record<Verdict, string> = {
  automate: "Automate",
  redesign: "Redesign",
  leave_as_is: "Leave as-is",
};

const styles: Record<Verdict, string> = {
  automate: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  redesign: "bg-amber-100 text-amber-800 ring-amber-200",
  leave_as_is: "bg-slate-100 text-slate-600 ring-slate-200",
};

export function VerdictBadge({ verdict }: { verdict: Verdict }) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ring-1 ${styles[verdict]}`}>{labels[verdict]}</span>;
}
