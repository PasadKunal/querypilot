interface Props {
  iterations: number;
  latency_ms: number;
  confidence: number;
  semantic_score: number | null;
  semantic_note: string | null;
  row_count: number;
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-slate-400 text-xs">{label}</span>
      <span className={`font-semibold text-sm ${color ?? "text-slate-800"}`}>{value}</span>
    </div>
  );
}

export default function MetaCard({ iterations, latency_ms, confidence, semantic_score, semantic_note, row_count }: Props) {
  const scoreColor =
    semantic_score === null
      ? "text-slate-400"
      : semantic_score >= 7
      ? "text-emerald-600"
      : "text-amber-600";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap gap-6">
        <Stat label="Rows returned" value={String(row_count)} />
        <Stat label="Iterations" value={`${iterations} / 3`} color={iterations > 1 ? "text-amber-600" : "text-emerald-600"} />
        <Stat label="Latency" value={`${(latency_ms / 1000).toFixed(2)}s`} />
        <Stat label="Confidence" value={`${Math.round(confidence * 100)}%`} />
        {semantic_score !== null && (
          <Stat label="Semantic score" value={`${semantic_score} / 10`} color={scoreColor} />
        )}
      </div>
      {semantic_note && (
        <p className="mt-3 text-slate-500 text-xs border-t border-slate-100 pt-3">
          {semantic_note}
        </p>
      )}
    </div>
  );
}
