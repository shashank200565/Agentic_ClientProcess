import { useEffect, useRef, useState, type ReactNode } from "react";

const labels: Record<string, string> = {
  repetitiveness: "Repetitiveness",
  judgment_need: "Judgment need",
  compliance_sensitivity: "Compliance sensitivity",
  ai_suitability: "AI suitability",
};
const MAX_PREVIEW_LENGTH = 220;
type Placement = "left" | "right" | "top" | "bottom";

export function ScoreTooltip({ dimension, explanation, children }: { dimension: string; explanation: string; children: ReactNode }) {
  const anchorRef = useRef<HTMLSpanElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [placement, setPlacement] = useState<Placement>("top");
  const truncated = explanation.length > MAX_PREVIEW_LENGTH ? `${explanation.slice(0, MAX_PREVIEW_LENGTH).trim()}...` : explanation;

  const open = isHovering || isPinned;
  const expanded = isPinned;

  useEffect(() => {
    if (!isPinned) return;
    const dismissOnOutsideClick = (event: MouseEvent) => {
      if (anchorRef.current && !anchorRef.current.contains(event.target as Node)) setIsPinned(false);
    };
    document.addEventListener("mousedown", dismissOnOutsideClick);
    return () => document.removeEventListener("mousedown", dismissOnOutsideClick);
  }, [isPinned]);

  useEffect(() => {
    if (!open || !anchorRef.current) return;
    const rect = anchorRef.current.getBoundingClientRect();
    const tooltipWidth = 300;
    const tooltipHeight = expanded ? 280 : 150;
    const gap = 12;
    const canTop = rect.top - tooltipHeight - gap >= 8;
    const canBottom = rect.bottom + tooltipHeight + gap <= window.innerHeight - 8;
    if (rect.right + tooltipWidth / 2 > window.innerWidth - 8 && rect.left - tooltipWidth - gap >= 8) setPlacement("left");
    else if (rect.left - tooltipWidth / 2 < 8 && rect.right + tooltipWidth + gap <= window.innerWidth - 8) setPlacement("right");
    else if (!canTop && canBottom) setPlacement("bottom");
    else setPlacement("top");
  }, [open, expanded]);

  const position = {
    top: "bottom-full left-1/2 mb-3 -translate-x-1/2",
    bottom: "left-1/2 top-full mt-3 -translate-x-1/2",
    left: "right-full top-1/2 mr-3 -translate-y-1/2",
    right: "left-full top-1/2 ml-3 -translate-y-1/2",
  }[placement];

  return <span ref={anchorRef} className="group relative inline-flex cursor-help" onMouseEnter={() => setIsHovering(true)} onMouseLeave={() => setIsHovering(false)} onFocus={() => setIsHovering(true)} onBlur={() => setIsHovering(false)} onClick={(event) => { event.stopPropagation(); setIsPinned((value) => !value); }}>
    {children}
    {open && <span role="tooltip" className={`pointer-events-none absolute ${position} z-[100] w-[min(300px,calc(100vw-1rem))] rounded-xl bg-[#102a2c] p-3 text-left text-xs font-normal leading-5 text-white shadow-[0_12px_35px_rgba(16,42,44,0.3)]`}><span className="mb-1 block font-semibold text-[#f2c14e]">{labels[dimension] ?? dimension.replaceAll("_", " ")}</span><span className={expanded ? "block max-h-56 overflow-y-auto" : "block"}>{expanded ? explanation : truncated}</span>{explanation.length > MAX_PREVIEW_LENGTH && <span className="mt-2 block text-[10px] font-semibold text-teal-100">{expanded ? "Pinned · click the score to collapse" : "Click the score to expand"}</span>}</span>}
  </span>;
}
