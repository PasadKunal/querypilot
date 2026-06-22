import { useState } from "react";
import { runQuery } from "../api/client";
import type { QueryResponse } from "../api/types";
import MetaCard from "../components/MetaCard";
import ResultsTable from "../components/ResultsTable";
import SQLBlock from "../components/SQLBlock";

const EXAMPLES = [
  { label: "Top customers", q: "Show the top 5 TPC-H customers by account balance" },
  { label: "Nations with most customers", q: "Which TPC-H nations have the most customers?" },
  { label: "Taxi fares by payment", q: "What is the average taxi fare by payment type?" },
  { label: "Northwind products", q: "List all Northwind products with their category names" },
];

function Spinner() {
  return (
    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
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

  return (
    <div className="flex flex-col h-full bg-slate-50">
      {/* Page header */}
      <div className="bg-white border-b border-slate-200 px-8 py-5">
        <h1 className="text-lg font-semibold text-slate-900">Natural Language Query</h1>
        <p className="text-sm text-slate-500 mt-0.5">Ask anything about your data in plain English</p>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto px-8 py-6 max-w-4xl w-full mx-auto">

        {/* Query input card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden mb-6">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKey}
            placeholder="e.g. Show me the top 5 customers by total order value across all orders"
            rows={4}
            className="w-full resize-none px-5 pt-4 pb-2 text-slate-800 placeholder-slate-300 text-sm focus:outline-none bg-transparent"
          />
          <div className="flex items-center justify-between px-5 py-3 border-t border-slate-100 bg-slate-50/60">
            <div className="flex flex-wrap gap-2">
              {EXAMPLES.map(({ label, q }) => (
                <button
                  key={label}
                  onClick={() => setQuestion(q)}
                  className="text-xs bg-white border border-slate-200 text-slate-500 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 px-3 py-1.5 rounded-lg transition-all"
                >
                  {label}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-3 ml-4 shrink-0">
              <span className="text-slate-300 text-xs hidden sm:block">⌘ + Enter</span>
              <button
                onClick={submit}
                disabled={loading || !question.trim()}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold px-5 py-2 rounded-xl transition-colors shadow-sm shadow-blue-200"
              >
                {loading && <Spinner />}
                {loading ? "Running..." : "Run Query"}
              </button>
            </div>
          </div>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex items-center gap-3 py-10 text-slate-400 justify-center">
            <Spinner />
            <span className="text-sm">Generating SQL and running query...</span>
          </div>
        )}

        {/* Error state */}
        {error && !loading && (
          <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl p-5 mb-6">
            <span className="text-lg leading-none mt-0.5">✗</span>
            <div>
              <p className="font-semibold text-sm mb-0.5">Query failed</p>
              <p className="text-red-500 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="flex flex-col gap-5">

            {/* Success banner */}
            {result.success && (
              <div className="flex items-center gap-2 text-emerald-700 text-sm font-medium">
                <span className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center text-xs">✓</span>
                Query executed successfully
              </div>
            )}

            {/* SQL block */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">Generated SQL</p>
              <SQLBlock sql={result.sql} />
            </div>

            {/* Reasoning */}
            {result.reasoning && (
              <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">Reasoning</p>
                <p className="text-slate-600 text-sm leading-relaxed">{result.reasoning}</p>
              </div>
            )}

            {/* Results table */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
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
      </div>
    </div>
  );
}
