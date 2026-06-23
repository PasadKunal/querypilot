import { useEffect, useState } from "react";
import { deleteSavedQuery, listConnections, listSavedQueries, listUserTables, runQuery, saveQuery, submitFeedback } from "../api/client";
import type { QueryResponse, SavedQuery, UserConnection, UserTable } from "../api/types";
import MetaCard from "../components/MetaCard";
import ResultChart from "../components/ResultChart";
import ResultsTable from "../components/ResultsTable";
import SQLBlock from "../components/SQLBlock";

const EXAMPLES = [
  { label: "⚡ Top customers", q: "Show the top 5 TPC-H customers by account balance" },
  { label: "🌍 Nations ranked", q: "Which TPC-H nations have the most customers?" },
  { label: "🚕 Taxi fares", q: "What is the average taxi fare by payment type?" },
  { label: "📦 Products", q: "List all Northwind products with their category names" },
];

const DATABASES = [
  {
    name: "Northwind",
    icon: "🛒",
    color: "from-violet-500 to-purple-600",
    bg: "bg-violet-50",
    border: "border-violet-100",
    desc: "Classic e-commerce dataset with customers, orders, products, and suppliers.",
    tables: ["nw_customers", "nw_orders", "nw_products", "nw_categories", "+ 4 more"],
  },
  {
    name: "TPC-H",
    icon: "📊",
    color: "from-blue-500 to-cyan-600",
    bg: "bg-blue-50",
    border: "border-blue-100",
    desc: "Industry-standard benchmark with supply chain, orders, and line items.",
    tables: ["tpch_customer", "tpch_orders", "tpch_lineitem", "tpch_nation", "+ 4 more"],
  },
  {
    name: "NYC Taxi",
    icon: "🚕",
    color: "from-amber-500 to-orange-500",
    bg: "bg-amber-50",
    border: "border-amber-100",
    desc: "New York City taxi trips with fares, zones, and payment types.",
    tables: ["nyc_trips", "nyc_taxi_zones", "nyc_payment_types", "nyc_rate_codes"],
  },
];

function Spinner() {
  return (
    <svg className="animate-spin w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}

export default function QueryPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userTables, setUserTables] = useState<UserTable[]>([]);
  const [connections, setConnections] = useState<UserConnection[]>([]);
  const [connectionId, setConnectionId] = useState<number | null>(null);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [bookmarked, setBookmarked] = useState(false);
  const [feedback, setFeedback] = useState<1 | 5 | null>(null);

  useEffect(() => {
    listUserTables().then(setUserTables).catch(() => {});
    listConnections().then(setConnections).catch(() => {});
    listSavedQueries().then(setSavedQueries).catch(() => {});
  }, []);

  const handleSave = async () => {
    if (!question.trim()) return;
    try {
      const saved = await saveQuery(question.trim());
      setSavedQueries((prev) => [saved, ...prev]);
      setBookmarked(true);
      setTimeout(() => setBookmarked(false), 2000);
    } catch { /* silent */ }
  };

  const handleDeleteSaved = async (id: number) => {
    await deleteSavedQuery(id);
    setSavedQueries((prev) => prev.filter((q) => q.id !== id));
  };

  const submit = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    setFeedback(null);
    try {
      const res = await runQuery({ question: question.trim(), connection_id: connectionId });
      setResult(res);
      if (!res.success) setError(res.error ?? "Query failed.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submit();
  };

  const runExample = (q: string) => {
    setQuestion(q);
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto">

      {/* ── Hero section ── */}
      <div className="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-800 px-8 pt-10 pb-8 shrink-0">
        <div>
          {/* Badge */}
          <div className="flex items-center gap-2 mb-5">
            <span className="inline-flex items-center gap-1.5 bg-blue-500/15 border border-blue-500/30 text-blue-300 text-xs font-medium px-3 py-1 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              {3 + connections.length} databases · {20 + userTables.length} tables · {connections.length + userTables.length > 0 ? "live" : "ready"}
            </span>
          </div>

          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
            Ask anything about your data
          </h1>
          <p className="text-slate-400 text-sm mb-7">
            Type a question in plain English. QueryPilot generates SQL, runs it, and validates the result.
          </p>

          {/* Connection selector */}
          {connections.length > 0 && (
            <div className="flex items-center gap-3 mb-4">
              <span className="text-slate-400 text-xs shrink-0">Query against:</span>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setConnectionId(null)}
                  className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-all ${
                    connectionId === null
                      ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                      : "bg-slate-800 text-slate-300 border-slate-700 hover:border-slate-500"
                  }`}
                >
                  Built-in databases
                </button>
                {connections.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setConnectionId(c.id)}
                    className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-all ${
                      connectionId === c.id
                        ? "bg-violet-600 text-white border-violet-600 shadow-sm"
                        : "bg-slate-800 text-slate-300 border-slate-700 hover:border-slate-500"
                    }`}
                  >
                    🔌 {c.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Query input */}
          <div className="bg-white rounded-2xl overflow-hidden shadow-2xl shadow-black/40">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKey}
              placeholder="e.g. Which TPC-H nations have the most customers? Show the top 5."
              rows={3}
              className="w-full resize-none px-5 pt-4 pb-3 text-slate-800 placeholder-slate-400 text-sm focus:outline-none bg-transparent leading-relaxed"
            />
            <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-t border-slate-100">
              <div className="flex flex-wrap gap-2">
                {EXAMPLES.map(({ label, q }) => (
                  <button
                    key={label}
                    onClick={() => runExample(q)}
                    className="text-xs bg-white border border-slate-200 text-slate-600 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 px-3 py-1.5 rounded-lg transition-all font-medium"
                  >
                    {label}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2 ml-3 shrink-0">
                <span className="text-slate-400 text-xs hidden md:block">⌘ Enter</span>
                <button
                  onClick={handleSave}
                  disabled={!question.trim()}
                  title="Save this query"
                  className={`flex items-center gap-1.5 text-sm px-3 py-2.5 rounded-xl border transition-all ${
                    bookmarked
                      ? "bg-amber-50 border-amber-300 text-amber-600"
                      : "bg-white border-slate-200 text-slate-500 hover:border-blue-300 hover:text-blue-600"
                  } disabled:opacity-30`}
                >
                  {bookmarked ? "★" : "☆"}
                </button>
                <button
                  onClick={submit}
                  disabled={loading || !question.trim()}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-all shadow-md shadow-blue-900/40"
                >
                  {loading ? <Spinner /> : <span>▶</span>}
                  {loading ? "Running..." : "Run Query"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Content area ── */}
      <div className="flex-1 bg-slate-50 px-8 py-8">
        <div>

          {/* Loading */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 gap-4">
              <div className="relative">
                <div className="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30 animate-pulse">
                  <span className="text-white text-xl">⚡</span>
                </div>
              </div>
              <div className="text-center">
                <p className="text-slate-700 font-semibold text-sm">Generating SQL...</p>
                <p className="text-slate-400 text-xs mt-1">Retrieving schema context and running query</p>
              </div>
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl p-5 mb-6 shadow-sm">
              <span className="text-xl leading-none">✗</span>
              <div>
                <p className="font-semibold text-sm mb-1">Query failed</p>
                <p className="text-red-500 text-sm leading-relaxed">{error}</p>
              </div>
            </div>
          )}

          {/* Results */}
          {result && !loading && (
            <div className="flex flex-col gap-6">
              {/* Success header */}
              {result.success && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-emerald-700 text-sm font-semibold">
                    <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-xs ring-1 ring-emerald-200">✓</span>
                    Query succeeded
                  </div>
                  <div className="flex items-center gap-3">
                    {result.query_id && (
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-slate-400">Helpful?</span>
                        {([5, 1] as const).map((r) => (
                          <button
                            key={r}
                            onClick={async () => {
                              setFeedback(r);
                              await submitFeedback(result.query_id!, r);
                            }}
                            className={`text-lg transition-all ${feedback === r ? "opacity-100 scale-110" : "opacity-40 hover:opacity-80"}`}
                          >
                            {r === 5 ? "👍" : "👎"}
                          </button>
                        ))}
                        {feedback && <span className="text-xs text-slate-400 ml-1">Thanks!</span>}
                      </div>
                    )}
                    <button
                      onClick={() => { setResult(null); setError(null); setQuestion(""); setFeedback(null); }}
                      className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              )}

              {/* SQL */}
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2.5">Generated SQL</p>
                <SQLBlock sql={result.sql} />
              </div>

              {/* Reasoning */}
              {result.reasoning && (
                <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">Agent Reasoning</p>
                  <p className="text-slate-600 text-sm leading-relaxed">{result.reasoning}</p>
                </div>
              )}

              {/* Insights */}
              {result.insights && (
                <div className="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-2xl border border-indigo-100 p-5 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">✨</span>
                    <p className="text-xs font-semibold text-indigo-600 uppercase tracking-widest">AI Insights</p>
                  </div>
                  <p className="text-slate-700 text-sm leading-relaxed">{result.insights}</p>
                  {result.suggested_questions.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-indigo-100">
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2.5">Suggested follow-ups</p>
                      <div className="flex flex-wrap gap-2">
                        {result.suggested_questions.map((q) => (
                          <button
                            key={q}
                            onClick={() => setQuestion(q)}
                            className="text-xs text-indigo-700 bg-white border border-indigo-200 hover:border-indigo-400 hover:bg-indigo-50 px-3 py-1.5 rounded-lg transition-all text-left"
                          >
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Chart */}
              {result.rows.length > 0 && (
                <ResultChart columns={result.columns} rows={result.rows} />
              )}

              {/* Table */}
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
                    Results: {result.row_count} {result.row_count === 1 ? "row" : "rows"}
                  </p>
                  <button
                    onClick={() => {
                      const header = result.columns.join(",");
                      const body = result.rows.map((r) =>
                        result.columns.map((c) => {
                          const v = r[c];
                          return v == null ? "" : String(v).includes(",") ? `"${String(v)}"` : String(v);
                        }).join(",")
                      ).join("\n");
                      const blob = new Blob([header + "\n" + body], { type: "text/csv" });
                      const a = document.createElement("a");
                      a.href = URL.createObjectURL(blob);
                      a.download = "results.csv";
                      a.click();
                    }}
                    className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-blue-600 border border-slate-200 hover:border-blue-300 px-3 py-1.5 rounded-lg transition-all bg-white"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Export CSV
                  </button>
                </div>
                <ResultsTable columns={result.columns} rows={result.rows} truncated={result.truncated} />
              </div>

              {/* Meta */}
              <MetaCard
                iterations={result.iterations}
                latency_ms={result.latency_ms}
                confidence={result.confidence}
                semantic_score={result.semantic_score}
                semantic_note={result.semantic_note}
                row_count={result.row_count}
              />
            </div>
          )}

          {/* Empty state – database cards */}
          {!result && !loading && !error && (
            <div className="flex flex-col gap-8">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Built-in Databases</p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {DATABASES.map((db) => (
                    <div key={db.name} className={`rounded-2xl border ${db.border} ${db.bg} p-5 flex flex-col gap-3`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${db.color} flex items-center justify-center text-lg shadow-sm`}>
                          {db.icon}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 text-sm">{db.name}</p>
                          <p className="text-slate-500 text-xs">{db.tables.length - 1} tables</p>
                        </div>
                      </div>
                      <p className="text-slate-600 text-xs leading-relaxed">{db.desc}</p>
                      <div className="flex flex-wrap gap-1.5">
                        {db.tables.map((t) => (
                          <span key={t} className="text-[10px] font-mono bg-white/70 border border-slate-200/80 text-slate-500 px-1.5 py-0.5 rounded">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {userTables.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Your Uploaded Tables</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {userTables.map((t) => (
                      <button
                        key={t.table_name}
                        onClick={() => setQuestion(`Show the first 10 rows of ${t.display_name}`)}
                        className="rounded-2xl border border-emerald-100 bg-emerald-50 p-5 flex flex-col gap-3 text-left hover:border-emerald-300 hover:bg-emerald-100/60 transition-all"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-emerald-500 flex items-center justify-center text-lg shadow-sm text-white">
                            📄
                          </div>
                          <div>
                            <p className="font-semibold text-slate-900 text-sm truncate max-w-[140px]">{t.display_name}</p>
                            <p className="text-slate-500 text-xs">{t.row_count.toLocaleString()} rows · {t.column_count} cols</p>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {t.columns.slice(0, 4).map((c) => (
                            <span key={c.name} className="text-[10px] font-mono bg-white/80 border border-emerald-200/80 text-slate-500 px-1.5 py-0.5 rounded">
                              {c.name}
                            </span>
                          ))}
                          {t.columns.length > 4 && (
                            <span className="text-[10px] text-slate-400">+{t.columns.length - 4}</span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {savedQueries.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Saved Queries</p>
                  <div className="flex flex-col gap-2">
                    {savedQueries.map((q) => (
                      <div key={q.id} className="flex items-center justify-between gap-3 bg-white border border-slate-200 rounded-xl px-4 py-3 group hover:border-blue-200 transition-colors">
                        <button
                          onClick={() => setQuestion(q.question)}
                          className="text-sm text-slate-700 text-left flex-1 truncate"
                        >
                          {q.question}
                        </button>
                        <button
                          onClick={() => handleDeleteSaved(q.id)}
                          className="text-slate-300 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100 shrink-0"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {userTables.length === 0 && (
                <div className="border-2 border-dashed border-slate-200 rounded-2xl p-6 flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-xl shrink-0">📂</div>
                  <div>
                    <p className="text-slate-700 text-sm font-medium">Upload your own CSV</p>
                    <p className="text-slate-400 text-xs mt-0.5">
                      Go to <span className="font-medium text-slate-500">Upload CSV</span> in the sidebar to add your own data and query it instantly.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
