import type { StaticWorkflowDiagram } from "../types/workflow";

export function WorkflowDiagram({ diagram }: { diagram: StaticWorkflowDiagram }) {
  const width = 900;
  const height = Math.max(180, diagram.nodes.length * 78);
  const positions = new Map(diagram.nodes.map((node, index) => [node.id, { x: 70, y: 35 + index * 70 }]));
  return <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-[#f8faf7] p-4">
    <svg viewBox={`0 0 ${width} ${height}`} className="min-w-[650px]" role="img" aria-label="Static workflow diagram">
      {diagram.edges.map((edge) => {
        const from = positions.get(edge.source);
        const to = positions.get(edge.target);
        if (!from || !to) return null;
        return <g key={`${edge.source}-${edge.target}`}>
          <line x1={from.x + 230} y1={from.y + 25} x2={to.x} y2={to.y + 25} stroke="#8ba8a1" strokeWidth="2" markerEnd="url(#arrow)" />
          {edge.label && <text x={from.x + 250} y={(from.y + to.y) / 2 + 22} fill="#64748b" fontSize="11">{edge.label}</text>}
        </g>;
      })}
      <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#8ba8a1" /></marker></defs>
      {diagram.nodes.map((node) => {
        const position = positions.get(node.id)!;
        return <g key={node.id}>
          <rect x={position.x} y={position.y} width="230" height="50" rx="12" fill={node.node_type === "human_checkpoint" ? "#fff4cf" : "#e4eee9"} stroke="#8ba8a1" />
          <text x={position.x + 14} y={position.y + 20} fill="#102a2c" fontSize="10" fontWeight="700">{node.node_type.replaceAll("_", " ").toUpperCase()}</text>
          <foreignObject x={position.x + 14} y={position.y + 25} width="202" height="22"><div style={{ fontSize: 11, color: "#334155", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{node.label}</div></foreignObject>
        </g>;
      })}
    </svg>
  </div>;
}
