import { useEffect, useRef, useState, type ReactNode } from "react";

const labels: Record<string, string> = { repetitiveness: "Repetitiveness", judgment_need: "Judgment need", compliance_sensitivity: "Compliance sensitivity", ai_suitability: "AI suitability" };
const MAX_PREVIEW_LENGTH = 220;
type Placement = "left" | "right" | "top" | "bottom";

export function ScoreTooltip({ dimension, explanation, children }: { dimension: string; explanation: string; children: ReactNode }) {
  const anchorRef = useRef<HTMLSpanElement>(null);
  const [open, setOpen] = useState(false);
  const [placement, setPlacement] = useState<Placement>("top");
  const truncated = explanation.length > MAX_PREVIEW_LENGTH ? `${explanation.slice(0, MAX_PREVIEW_LENGTH).trim()}...` : explanation;
  useEffect(() => {
    if (!open || !anchorRef.current) return;
    const rect = anchorRef.current.getBoundingClientRect();
    const width = 300;
    const height = 150;
    if (rect.right + width / 2 > window.innerWidth - 8 && rect.left - width - 12 >= 8) setPlacement("left");
    else if (rect.left - width / 2 < 8 && rect.right + width + 12 <= window.innerWidth - 8) setPlacement("right");
    else if (rect.top - height - 12 < 8 && rect.bottom + height + 12 <= window.innerHeight - 8) setPlacement("bottom");
    else setPlacement("top");
  }, [open]);
  const position = { top: "bottom-full left-1/2 mb-3 -translate-x-1/2", bottom: "left-1/2 top-full mt-3 -translate-x-1/2", left: "right-full top-1/2 mr-3 -translate-y-1/2", right: "left-full top-1/2 ml-3 -translate-y-1/2" }[placement];
  return <span ref={anchorRef} className="group relative inline-flex cursor-help" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)} onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}>{children}{open && <span role="tooltip" className={`pointer-events-none absolute ${position} z-[100] w-[min(300px,calc(100vw-1rem))] rounded-xl bg-[#102a2c] p-3 text-left text-xs font-normal leading-5 text-white shadow-[0_12px_35px_rgba(16,42,44,0.3)]`}><span className="mb-1 block font-semibold text-[#f2c14e]">{labels[dimension] ?? dimension.replaceAll("_", " ")}</span>{truncated}</span>}</span>;
}
