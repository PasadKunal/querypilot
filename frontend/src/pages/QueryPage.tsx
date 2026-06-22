import { useState } from "react";
import { runQuery } from "../api/client";
import type { QueryResponse } from "../api/types";
import MetaCard from "../components/MetaCard";
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

  const submit = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await runQuery({ question: question.trim() });
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
              3 live databases · 20 tables · 140 schema chunks
            </span>
          </div>

          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
            Ask anything about your data
          </h1>
          <p className="text-slate-400 text-sm mb-7">
            Type a question in plain English. QueryPilot generates SQL, runs it, and validates the result.
          </p>

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
              <div className="flex items-center gap-3 ml-3 shrink-0">
                <span className="text-slate-400 text-xs hidden md:block">⌘ Enter</span>
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
                  <button
                    onClick={() => { setResult(null); setError(null); setQuestion(""); }}
                    className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    Clear
                  </button>
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

              {/* Table */}
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2.5">
                  Results — {result.row_count} {result.row_count === 1 ? "row" : "rows"}
                </p>
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
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Available Databases</p>
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
          )}
        </div>
      </div>
    </div>
  );
}
