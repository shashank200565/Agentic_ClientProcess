import { useEffect, useRef, useState, type ReactNode } from "react";

const labels: Record<string, string> = { repetitiveness: "Repetitiveness", judgment_need: "Judgment need", compliance_sensitivity: "Compliance sensitivity", ai_suitability: "AI suitability" };
const MAX_PREVIEW_LENGTH = 220;

export function ScoreTooltip({ dimension, explanation, children }: { dimension: string; explanation: string; children: ReactNode }) {
  const anchorRef = useRef<HTMLSpanElement>(null); const [open, setOpen] = useState(false); const [position, setPosition] = useState({ left: 0, top: 0 });
  const truncated = explanation.length > MAX_PREVIEW_LENGTH ? `${explanation.slice(0, MAX_PREVIEW_LENGTH).trim()}...` : explanation;
  useEffect(() => {
    if (!open || !anchorRef.current) return;
    const rect = anchorRef.current.getBoundingClientRect(); const width = Math.min(300, window.innerWidth - 16); const height = 150; const gap = 12;
    const preferredTop = rect.top - height - gap; const top = preferredTop >= 8 ? preferredTop : Math.min(window.innerHeight - height - 8, rect.bottom + gap);
    const left = Math.max(8, Math.min(window.innerWidth - width - 8, rect.left + rect.width / 2 - width / 2));
    setPosition({ left, top });
  }, [open]);
  return <span ref={anchorRef} className="group relative inline-flex cursor-help" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)} onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}>{children}{open && <span role="tooltip" style={{ left: position.left, top: position.top }} className="pointer-events-none fixed z-[100] max-h-[min(220px,calc(100vh-1rem))] w-[min(300px,calc(100vw-1rem))] overflow-y-auto rounded-xl bg-[#102a2c] p-3 text-left text-xs font-normal leading-5 text-white shadow-[0_12px_35px_rgba(16,42,44,0.3)]"><span className="mb-1 block font-semibold text-[#f2c14e]">{labels[dimension] ?? dimension.replaceAll("_", " ")}</span>{truncated}</span>}</span>;
}
