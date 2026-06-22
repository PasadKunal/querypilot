import { useEffect, useState } from "react";
import { fetchHistory } from "../api/client";
import type { HistoryEntry } from "../api/types";

export default function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory()
      .then(setEntries)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-5xl mx-auto w-full">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Query History</h2>
        <p className="text-slate-500 text-sm mt-1">Last 50 queries logged by the agent.</p>
      </div>

      {loading && <p className="text-slate-400 text-sm">Loading...</p>}
      {error && <p className="text-red-500 text-sm">{error}</p>}

      {!loading && !error && entries.length === 0 && (
        <p className="text-slate-400 text-sm">No queries yet. Run one from the Query page.</p>
      )}

      {!loading && entries.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 font-semibold text-slate-600">Question</th>
                <th className="px-4 py-3 font-semibold text-slate-600 text-center">Status</th>
                <th className="px-4 py-3 font-semibold text-slate-600 text-center">Iterations</th>
                <th className="px-4 py-3 font-semibold text-slate-600 text-center">Rows</th>
                <th className="px-4 py-3 font-semibold text-slate-600 text-center">Score</th>
                <th className="px-4 py-3 font-semibold text-slate-600 text-right">Latency</th>
                <th className="px-4 py-3 font-semibold text-slate-600 text-right">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {entries.map((e) => (
                <tr key={e.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 text-slate-800 max-w-xs">
                    <p className="truncate" title={e.question}>{e.question}</p>
                    {e.final_sql && (
                      <code className="text-slate-400 text-xs block truncate font-mono mt-0.5" title={e.final_sql}>
                        {e.final_sql}
                      </code>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${e.success ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                      {e.success ? "OK" : "Failed"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-slate-500">{e.iterations}</td>
                  <td className="px-4 py-3 text-center text-slate-500">{e.row_count ?? "-"}</td>
                  <td className="px-4 py-3 text-center">
                    {e.semantic_score !== null ? (
                      <span className={`font-semibold ${e.semantic_score >= 7 ? "text-emerald-600" : "text-amber-600"}`}>
                        {e.semantic_score}/10
                      </span>
                    ) : (
                      <span className="text-slate-300">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-500">
                    {e.latency_ms ? `${(e.latency_ms / 1000).toFixed(2)}s` : "-"}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-400 text-xs whitespace-nowrap">
                    {new Date(e.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
