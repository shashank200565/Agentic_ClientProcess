import { Link } from "react-router-dom";

interface PlaceholderPageProps {
  eyebrow: string;
  title: string;
  description: string;
  dependency: string;
}

export function PlaceholderPage({ eyebrow, title, description, dependency }: PlaceholderPageProps) {
  return <section className="mx-auto flex min-h-[60vh] max-w-3xl items-center"><div className="w-full rounded-[2rem] border border-dashed border-slate-300 bg-white p-8 sm:p-12"><span className="inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800 ring-1 ring-amber-200">Placeholder · backend pending</span><p className="mt-10 text-sm font-semibold uppercase tracking-[0.22em] text-teal-700">{eyebrow}</p><h1 className="mt-4 max-w-xl font-display text-4xl font-semibold tracking-tight text-[#102a2c]">{title}</h1><p className="mt-5 max-w-xl text-lg leading-8 text-slate-600">{description}</p><div className="mt-8 rounded-xl bg-slate-50 p-4 text-sm text-slate-500"><span className="font-semibold text-slate-700">Waiting on:</span> {dependency}</div><Link to="/" className="mt-8 inline-flex rounded-xl bg-[#102a2c] px-5 py-3 text-sm font-semibold text-white">Return to upload</Link></div></section>;
}
