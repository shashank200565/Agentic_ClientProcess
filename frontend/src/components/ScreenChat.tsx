import { useState } from "react";
import { askScreenChat, type ScreenChatMessage } from "../api/workflows";

export function ScreenChat({ context }: { context: Record<string, unknown> }) {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ScreenChatMessage[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState("");

  async function ask() {
    const currentQuestion = question.trim();
    if (!currentQuestion) return;
    setIsAsking(true); setError("");
    try {
      const answer = await askScreenChat(currentQuestion, context, messages);
      setMessages((previous) => [...previous, { role: "user", content: currentQuestion }, { role: "assistant", content: answer }]);
      setQuestion("");
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "The screen assistant failed."); }
    finally { setIsAsking(false); }
  }

  return <div className="fixed bottom-5 right-5 z-50 w-[min(380px,calc(100vw-2rem))]">
    {isOpen && <div className="mb-3 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_18px_60px_rgba(16,42,44,0.18)]"><div className="flex items-center justify-between bg-[#102a2c] px-4 py-3 text-white"><div><p className="font-display font-semibold">Screen assistant</p><p className="text-[11px] text-teal-100">Grounded in this screen's stored analysis</p></div><button type="button" onClick={() => setIsOpen(false)} className="text-lg text-slate-300 hover:text-white" aria-label="Close screen assistant">×</button></div><div className="max-h-72 space-y-3 overflow-y-auto p-4">{messages.length === 0 && <p className="text-sm leading-6 text-slate-500">Ask why a step received its verdict, what its scores mean, or whether a different path would create a control tension.</p>}{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`rounded-xl p-3 text-sm leading-6 ${message.role === "user" ? "ml-8 bg-[#102a2c] text-white" : "mr-4 bg-[#f6f7f2] text-slate-700"}`}><p className="mb-1 text-[10px] font-semibold uppercase tracking-wide opacity-60">{message.role === "user" ? "You" : "Assistant"}</p>{message.role === "assistant" ? <ul className="space-y-1">{message.content.split(/\n+/).map((line, lineIndex) => <li key={lineIndex} className="flex gap-2"><span>•</span><span>{line.replace(/^[-*•]\s*/, "")}</span></li>)}</ul> : message.content}</div>)}{error && <p className="rounded-lg bg-red-50 p-3 text-xs leading-5 text-red-700">{error}</p>}</div><div className="border-t border-slate-200 p-3"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void ask(); } }} rows={2} placeholder="Ask about this screen..." className="w-full resize-none rounded-xl border border-slate-200 px-3 py-2 text-sm leading-5 outline-none focus:ring-2 focus:ring-teal-600" /><button type="button" disabled={isAsking || !question.trim()} onClick={() => void ask()} className="mt-2 w-full rounded-xl bg-[#102a2c] px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">{isAsking ? "Thinking..." : "Ask assistant"}</button></div></div>}
    <button type="button" onClick={() => setIsOpen((open) => !open)} className="ml-auto flex items-center gap-2 rounded-full bg-[#102a2c] px-4 py-3 text-sm font-semibold text-white shadow-[0_10px_30px_rgba(16,42,44,0.2)] hover:bg-teal-900"><span className="grid h-6 w-6 place-items-center rounded-full bg-[#f2c14e] text-xs font-bold text-[#102a2c]">?</span>{isOpen ? "Close assistant" : "Ask about this screen"}</button>
  </div>;
}
