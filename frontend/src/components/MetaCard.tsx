interface Props {
  iterations: number;
  latency_ms: number;
  confidence: number;
  semantic_score: number | null;
  semantic_note: string | null;
  row_count: number;
}

interface PillProps { label: string; value: string; variant: "default" | "success" | "warning" | "info" }

function Pill({ label, value, variant }: PillProps) {
  const colors = {
    default: "bg-slate-100 text-slate-700",
    success: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
    warning: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
    info:    "bg-blue-50 text-blue-700 ring-1 ring-blue-200",
  };
  return (
    <div className={`flex flex-col items-center px-4 py-3 rounded-xl ${colors[variant]}`}>
      <span className="font-bold text-lg leading-none">{value}</span>
      <span className="text-[11px] font-medium mt-1 opacity-70">{label}</span>
    </div>
  );
}

export default function MetaCard({ iterations, latency_ms, confidence, semantic_score, semantic_note, row_count }: Props) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Query Metadata</p>
      <div className="flex flex-wrap gap-3">
        <Pill label="Rows" value={String(row_count)} variant="info" />
        <Pill
          label="Iterations"
          value={`${iterations} / 3`}
          variant={iterations > 1 ? "warning" : "success"}
        />
        <Pill label="Latency" value={`${(latency_ms / 1000).toFixed(2)}s`} variant="default" />
        <Pill label="Confidence" value={`${Math.round(confidence * 100)}%`} variant="default" />
        {semantic_score !== null && (
          <Pill
            label="Semantic"
            value={`${semantic_score}/10`}
            variant={semantic_score >= 7 ? "success" : "warning"}
          />
        )}
      </div>
      {semantic_note && (
        <p className="mt-4 text-slate-500 text-xs leading-relaxed border-t border-slate-100 pt-4">
          {semantic_note}
        </p>
      )}
    </div>
  );
}
