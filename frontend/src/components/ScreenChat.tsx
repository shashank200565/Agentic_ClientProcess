import { useState, type ReactNode } from "react";
import { askScreenChat, type ScreenChatMessage } from "../api/workflows";

function renderInlineMarkdown(text: string): ReactNode[] {
  const parts: ReactNode[] = [];
  const pattern = /(\*\*[^*\n]+\*\*|__[^_\n]+__|\*[^*\n]+\*|_[^_\n]+_|`[^`\n]+`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) parts.push(text.slice(lastIndex, match.index));
    const token = match[0];
    const isCode = token.startsWith("`");
    const isStrong = token.startsWith("**") || token.startsWith("__");
    const content = token.slice(isCode || !isStrong ? 1 : 2, isCode || !isStrong ? -1 : -2);
    const key = `${match.index}-${token}`;

    if (isStrong) {
      parts.push(<strong key={key}>{content}</strong>);
    } else if (isCode) {
      parts.push(<code key={key} className="rounded bg-white/70 px-1 py-0.5 font-mono text-[0.9em]">{content}</code>);
    } else {
      parts.push(<em key={key}>{content}</em>);
    }
    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) parts.push(text.slice(lastIndex));
  return parts;
}

function AssistantMarkdown({ content }: { content: string }) {
  return (
    <ul className="space-y-1">
      {content.split(/\n+/).map((line, lineIndex) => (
        <li key={lineIndex} className="flex gap-2">
          <span>•</span>
          <span>{renderInlineMarkdown(line.replace(/^[-*•]\s*/, ""))}</span>
        </li>
      ))}
    </ul>
  );
}

export function ScreenChat({ context }: { context: Record<string, unknown> }) {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ScreenChatMessage[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState("");

  async function ask() {
    const currentQuestion = question.trim();
    if (!currentQuestion) return;
    setIsAsking(true);
    setError("");

    try {
      const answer = await askScreenChat(currentQuestion, context, messages);
      setMessages((previous) => [
        ...previous,
        { role: "user", content: currentQuestion },
        { role: "assistant", content: answer },
      ]);
      setQuestion("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "The screen assistant failed.");
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <div className="fixed bottom-5 right-5 z-50 w-[min(380px,calc(100vw-2rem))]">
      {isOpen && (
        <div className="mb-3 overflow-hidden rounded-[24px] border border-blue-100 bg-white shadow-float">
          <div className="flex items-center justify-between bg-brand-radial px-4 py-3 text-white">
            <div>
              <p className="font-display font-semibold">Screen assistant</p>
              <p className="text-[11px] text-blue-100">Grounded in this screen&apos;s stored analysis</p>
            </div>
            <button type="button" onClick={() => setIsOpen(false)} className="text-lg text-blue-100 hover:text-white" aria-label="Close screen assistant">×</button>
          </div>
          <div className="max-h-72 space-y-3 overflow-y-auto p-4">
            {messages.length === 0 && <p className="text-sm leading-6 text-slate-500">Ask why a step received its verdict, what its scores mean, or whether a different path would create a control tension.</p>}
            {messages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`rounded-2xl p-3 text-sm leading-6 ${message.role === "user" ? "ml-8 bg-[#0d1834] text-white" : "mr-4 bg-blue-50 text-slate-700"}`}>
                <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide opacity-60">{message.role === "user" ? "You" : "Assistant"}</p>
                {message.role === "assistant" ? <AssistantMarkdown content={message.content} /> : message.content}
              </div>
            ))}
            {error && <p className="rounded-lg bg-red-50 p-3 text-xs leading-5 text-red-700">{error}</p>}
          </div>
          <div className="border-t border-blue-100 p-3">
            <textarea value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void ask(); } }} rows={2} placeholder="Ask about this screen..." className="w-full resize-none rounded-2xl border border-blue-100 px-4 py-2 text-sm leading-5 outline-none focus:ring-2 focus:ring-brand" />
            <button type="button" onClick={() => void ask()} disabled={isAsking || !question.trim()} className="mt-2 w-full rounded-full bg-brand px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-deep disabled:cursor-not-allowed disabled:opacity-50">{isAsking ? "Thinking..." : "Ask assistant"}</button>
          </div>
        </div>
      )}
      <button type="button" onClick={() => setIsOpen((open) => !open)} className="ml-auto flex rounded-full bg-brand px-4 py-3 text-sm font-semibold text-white shadow-float transition hover:bg-brand-deep">{isOpen ? "Close assistant" : "Ask assistant"}</button>
    </div>
  );
}
