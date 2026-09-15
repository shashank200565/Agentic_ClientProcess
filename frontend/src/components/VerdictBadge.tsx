import type { Verdict } from "../types/workflow";

const labels: Record<Verdict, string> = {
  automate: "Automate",
  redesign: "Redesign",
  leave_as_is: "Leave as-is",
};

const styles: Record<Verdict, string> = {
  automate: "bg-blue-50 text-blue-700 ring-blue-200",
  redesign: "bg-violet-50 text-violet-700 ring-violet-200",
  leave_as_is: "bg-slate-100 text-slate-700 ring-slate-200",
};

const icons: Record<Verdict, string> = { automate: "↗", redesign: "✦", leave_as_is: "—" };

export function VerdictBadge({ verdict }: { verdict: Verdict }) {
  return <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ring-1 ${styles[verdict]}`}><span aria-hidden="true" className="font-bold">{icons[verdict]}</span>{labels[verdict]}</span>;
}
