import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { extractWorkflow, scoreWorkflow } from "../api/workflows";

export function UploadPage() {
  const navigate = useNavigate();
  const fileInput = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [text, setText] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingPhase, setLoadingPhase] = useState<"extracting" | "scoring" | null>(null);

  async function handleSubmit() {
    if (!file && !text.trim()) {
      setError("Choose a PDF or paste a workflow description first.");
      return;
    }
    setError("");
    setIsLoading(true);
    try {
      setLoadingPhase("extracting");
      const extractedWorkflow = file
        ? await extractWorkflow(file)
        : await extractWorkflow({ text, name: name || "Pasted workflow" });
      setLoadingPhase("scoring");
      const workflow = await scoreWorkflow(extractedWorkflow);
      sessionStorage.setItem("currentWorkflow", JSON.stringify(workflow));
      navigate(`/review/${workflow.workflow_id}`);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Extraction failed.");
    } finally {
      setIsLoading(false);
      setLoadingPhase(null);
    }
  }

  return (
    <section className="mx-auto max-w-6xl">
      <div className="grid gap-8 pt-1 xl:grid-cols-[1.05fr_0.95fr] xl:items-start xl:gap-14">
        <div>
          <p className="mb-5 inline-flex rounded-full bg-blue-50 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.22em] text-brand">01 / Bring in the work</p>
          <h1 className="max-w-3xl font-display text-5xl font-semibold leading-[1.03] tracking-tight text-ink sm:text-6xl">Every workflow has a shape. Let&apos;s make it visible.</h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">Upload an SOP or paste a step list. The extraction layer will turn the document into a clean sequence you can inspect before any scoring begins.</p>
        </div>
        <div className="rounded-[28px] bg-brand-radial p-7 text-white shadow-float sm:p-9">
          <div className="mb-10 flex items-center justify-between">
            <span className="text-sm font-semibold">Workflow intake</span>
            <span className="rounded-full bg-white/15 px-3 py-1 text-xs text-blue-100">Live extraction</span>
          </div>
          <button type="button" onClick={() => fileInput.current?.click()} className="group w-full rounded-[22px] border border-dashed border-white/40 bg-white/10 px-6 py-10 text-left transition hover:border-white hover:bg-white/20">
            <input ref={fileInput} className="hidden" type="file" accept=".pdf,.txt,application/pdf,text/plain" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            <span className="mb-5 grid h-11 w-11 place-items-center rounded-full bg-white text-xl text-brand">↑</span>
            <span className="block font-display text-xl font-semibold">{file ? file.name : "Drop an SOP here"}</span>
            <span className="mt-2 block text-sm text-blue-100">PDF or text file · extraction is powered by the real backend route</span>
          </button>
          <div className="my-5 flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400"><span className="h-px flex-1 bg-slate-300" />or<span className="h-px flex-1 bg-slate-300" /></div>
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Workflow name (optional)" className="mb-3 w-full rounded-full border border-white/30 bg-white px-4 py-3 text-sm text-ink outline-none ring-brand transition placeholder:text-slate-400 focus:ring-2" />
          <textarea value={text} onChange={(event) => { setText(event.target.value); setFile(null); }} placeholder="Paste a workflow description..." rows={4} className="w-full resize-none rounded-[22px] border border-white/30 bg-white px-4 py-3 text-sm leading-6 text-ink outline-none ring-brand transition placeholder:text-slate-400 focus:ring-2" />
          {error && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs leading-5 text-red-700">{error}</p>}
          <button type="button" onClick={handleSubmit} disabled={isLoading} className="mt-4 flex w-full items-center justify-center gap-2 rounded-full bg-white px-5 py-3.5 text-sm font-bold text-brand transition hover:bg-blue-50 disabled:cursor-wait disabled:opacity-60">
            {isLoading && <span aria-hidden="true" className="h-4 w-4 animate-spin rounded-full border-2 border-brand/30 border-t-brand" />}
            {loadingPhase === "extracting" ? "Extracting workflow steps..." : loadingPhase === "scoring" ? "Scoring workflow steps..." : "Extract and score workflow"}
          </button>
          {isLoading && <p className="mt-3 text-center text-xs leading-5 text-slate-500" aria-live="polite">{loadingPhase === "extracting" ? "Reading the document and organizing its current-state steps." : "Applying the Decision Engine to each step. This can take a little while for a live model call."}</p>}
        </div>
      </div>
    </section>
  );
}
