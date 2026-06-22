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
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Dark header to match Query page style */}
      <div className="bg-gradient-to-b from-slate-950 to-slate-900 px-8 pt-10 pb-8 shrink-0">
        <div className="max-w-5xl mx-auto">
          <span className="inline-flex items-center gap-1.5 bg-blue-500/15 border border-blue-500/30 text-blue-300 text-xs font-medium px-3 py-1 rounded-full mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
            Query log
          </span>
          <h1 className="text-2xl font-bold text-white mb-1">Query History</h1>
          <p className="text-slate-400 text-sm">Every query the agent has run, with SQL, score, and latency.</p>
        </div>
      </div>

      <div className="flex-1 bg-slate-50 px-8 py-8 max-w-5xl w-full mx-auto">

        {loading && (
          <div className="flex items-center gap-2.5 text-slate-400 py-10 justify-center">
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            <span className="text-sm">Loading history...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-2xl p-5">
            {error}
          </div>
        )}

        {!loading && !error && entries.length === 0 && (
          <div className="text-center py-20">
            <p className="text-3xl mb-3">🕓</p>
            <p className="text-slate-500 text-sm">No queries yet.</p>
            <p className="text-slate-400 text-xs mt-1">Run a query from the Query page to see it here.</p>
          </div>
        )}

        {!loading && entries.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="px-5 py-3.5 font-semibold text-xs text-slate-500 uppercase tracking-wider">Question</th>
                    <th className="px-4 py-3.5 font-semibold text-xs text-slate-500 uppercase tracking-wider text-center">Status</th>
                    <th className="px-4 py-3.5 font-semibold text-xs text-slate-500 uppercase tracking-wider text-center">Iters</th>
                    <th className="px-4 py-3.5 font-semibold text-xs text-slate-500 uppercase tracking-wider text-center">Rows</th>
                    <th className="px-4 py-3.5 font-semibold text-xs text-slate-500 uppercase tracking-wider text-center">Score</th>
                    <th className="px-4 py-3.5 font-semibold text-xs text-slate-500 uppercase tracking-wider text-right">Latency</th>
                    <th className="px-5 py-3.5 font-semibold text-xs text-slate-500 uppercase tracking-wider text-right">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {entries.map((e) => (
                    <tr key={e.id} className="hover:bg-slate-50/80 transition-colors group">
                      <td className="px-5 py-4 max-w-sm">
                        <p className="text-slate-800 font-medium truncate text-sm" title={e.question}>{e.question}</p>
                        {e.final_sql && (
                          <p className="text-slate-400 text-xs font-mono truncate mt-0.5" title={e.final_sql}>
                            {e.final_sql}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-4 text-center">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                          e.success
                            ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200"
                            : "bg-red-50 text-red-700 ring-1 ring-red-200"
                        }`}>
                          {e.success ? "✓ OK" : "✗ Failed"}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-center text-slate-500 text-sm">{e.iterations}</td>
                      <td className="px-4 py-4 text-center text-slate-500 text-sm">{e.row_count ?? <span className="text-slate-300">—</span>}</td>
                      <td className="px-4 py-4 text-center text-sm">
                        {e.semantic_score !== null ? (
                          <span className={`font-semibold ${e.semantic_score >= 7 ? "text-emerald-600" : "text-amber-600"}`}>
                            {e.semantic_score}/10
                          </span>
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                      <td className="px-4 py-4 text-right text-slate-500 text-sm">
                        {e.latency_ms ? `${(e.latency_ms / 1000).toFixed(2)}s` : <span className="text-slate-300">—</span>}
                      </td>
                      <td className="px-5 py-4 text-right text-slate-400 text-xs whitespace-nowrap">
                        {new Date(e.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
