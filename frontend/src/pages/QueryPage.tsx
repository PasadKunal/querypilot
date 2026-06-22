import { useState } from "react";
import { runQuery } from "../api/client";
import type { QueryResponse } from "../api/types";
import MetaCard from "../components/MetaCard";
import ResultsTable from "../components/ResultsTable";
import SQLBlock from "../components/SQLBlock";

const EXAMPLE_QUESTIONS = [
  "Show the top 5 customers by total order value",
  "Which TPC-H nations have the most customers?",
  "What are the average taxi fares by payment type?",
  "List all Northwind products with their category names",
];

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
    <div className="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Natural Language Query</h2>
        <p className="text-slate-500 text-sm mt-1">
          Ask a question in plain English. QueryPilot generates and runs the SQL for you.
        </p>
      </div>

      {/* Input */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-4 shadow-sm">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKey}
          placeholder="e.g. Show me the top 5 customers by total order value"
          rows={3}
          className="w-full resize-none text-slate-800 placeholder-slate-300 text-sm focus:outline-none"
        />
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
          <span className="text-slate-300 text-xs">⌘ + Enter to run</span>
          <button
            onClick={submit}
            disabled={loading || !question.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
          >
            {loading ? "Running..." : "Run Query"}
          </button>
        </div>
      </div>

      {/* Example questions */}
      {!result && !loading && (
        <div className="mb-8">
          <p className="text-xs text-slate-400 mb-2 uppercase tracking-wider">Try an example</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                className="text-xs bg-white border border-slate-200 text-slate-600 hover:border-blue-400 hover:text-blue-600 px-3 py-1.5 rounded-full transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-3 py-8 text-slate-400">
          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <span className="text-sm">Generating SQL and running query...</span>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm mb-4">
          <p className="font-semibold mb-1">Query failed</p>
          <p className="text-red-500">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="flex flex-col gap-5">
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-2">Generated SQL</p>
            <SQLBlock sql={result.sql} />
          </div>

          {result.reasoning && (
            <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Reasoning</p>
              <p className="text-slate-600 text-sm">{result.reasoning}</p>
            </div>
          )}

          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-2">
              Results ({result.row_count} rows)
            </p>
            <ResultsTable
              columns={result.columns}
              rows={result.rows}
              truncated={result.truncated}
            />
          </div>

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
  );
}
