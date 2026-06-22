import { useCallback, useEffect, useRef, useState } from "react";
import { deleteUserTable, listUserTables, uploadCSV } from "../api/client";
import type { UserTable } from "../api/types";

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

function PG_BADGE({ type }: { type: string }) {
  const color =
    type === "BIGINT" || type === "NUMERIC"
      ? "bg-blue-50 text-blue-700 ring-blue-200"
      : type === "TIMESTAMP" || type === "DATE"
      ? "bg-violet-50 text-violet-700 ring-violet-200"
      : type === "BOOLEAN"
      ? "bg-amber-50 text-amber-700 ring-amber-200"
      : "bg-slate-100 text-slate-600 ring-slate-200";
  return (
    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ring-1 ${color}`}>
      {type}
    </span>
  );
}

export default function UploadPage() {
  const [tables, setTables] = useState<UserTable[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const loadTables = useCallback(async () => {
    try {
      const data = await listUserTables();
      setTables(data);
    } catch {
      // silently fail on list error
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => { loadTables(); }, [loadTables]);

  const handleFile = useCallback(async (file: File) => {
    const name = file.name.toLowerCase();
    if (!name.endsWith(".csv") && !name.endsWith(".xlsx") && !name.endsWith(".xls")) {
      setError("Only .csv, .xlsx, and .xls files are supported");
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      setError("File too large — max 20 MB");
      return;
    }
    setError(null);
    setUploading(true);
    setUploadProgress(`Uploading ${file.name} (${formatBytes(file.size)})...`);
    try {
      setUploadProgress("Parsing CSV and inferring column types...");
      const table = await uploadCSV(file);
      setUploadProgress(`Embedding schema (${table.column_count} columns)...`);
      await loadTables();
      setUploadProgress(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
      setUploadProgress(null);
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }, [loadTables]);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const onDelete = async (tableName: string) => {
    setDeletingId(tableName);
    try {
      await deleteUserTable(tableName);
      setTables((prev) => prev.filter((t) => t.table_name !== tableName));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="bg-gradient-to-b from-slate-950 to-slate-900 px-8 pt-10 pb-8 shrink-0">
        <span className="inline-flex items-center gap-1.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-medium px-3 py-1 rounded-full mb-4">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Bring your own data
        </span>
        <h1 className="text-2xl font-bold text-white mb-1">Upload CSV</h1>
        <p className="text-slate-400 text-sm">
          Upload any CSV file. QueryPilot creates a table, embeds the schema, and lets you query it in plain English.
        </p>
      </div>

      <div className="flex-1 bg-slate-50 px-8 py-8 flex flex-col gap-8">

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => !uploading && inputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl flex flex-col items-center justify-center py-14 px-6 transition-all cursor-pointer select-none ${
            dragOver
              ? "border-blue-400 bg-blue-50"
              : uploading
              ? "border-slate-200 bg-slate-50 cursor-default"
              : "border-slate-200 bg-white hover:border-blue-300 hover:bg-blue-50/30"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
          />

          {uploading ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-blue-100 flex items-center justify-center animate-pulse">
                <span className="text-2xl">⚡</span>
              </div>
              <p className="text-slate-700 font-semibold text-sm">{uploadProgress}</p>
              <p className="text-slate-400 text-xs">This may take 10-30 seconds while we embed the schema</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 text-center">
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-2xl transition-colors ${
                dragOver ? "bg-blue-100" : "bg-slate-100"
              }`}>
                📂
              </div>
              <div>
                <p className="text-slate-700 font-semibold text-sm">
                  Drop a CSV file here, or <span className="text-blue-600">browse</span>
                </p>
                <p className="text-slate-400 text-xs mt-1">CSV, Excel (.xlsx) · up to 20 MB · 50,000 rows</p>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl p-4 text-sm">
            <span className="text-lg leading-none">✗</span>
            <span>{error}</span>
          </div>
        )}

        {/* Uploaded tables */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
              Uploaded Tables {tables.length > 0 && `· ${tables.length}`}
            </p>
            {tables.length > 0 && (
              <p className="text-xs text-slate-400">All queryable from the Query page</p>
            )}
          </div>

          {loadingList && (
            <div className="flex items-center gap-2 text-slate-400 text-sm py-4">
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Loading...
            </div>
          )}

          {!loadingList && tables.length === 0 && (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-2xl">
              <p className="text-3xl mb-3">🗂</p>
              <p className="text-slate-500 text-sm font-medium">No tables uploaded yet</p>
              <p className="text-slate-400 text-xs mt-1">Upload a CSV above to get started</p>
            </div>
          )}

          {tables.length > 0 && (
            <div className="flex flex-col gap-3">
              {tables.map((t) => (
                <div
                  key={t.table_name}
                  className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 flex flex-col gap-3"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center text-lg shrink-0">
                        📄
                      </div>
                      <div className="min-w-0">
                        <p className="font-semibold text-slate-900 text-sm truncate">{t.display_name}</p>
                        <p className="text-slate-400 text-xs font-mono mt-0.5">{t.table_name}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => onDelete(t.table_name)}
                      disabled={deletingId === t.table_name}
                      className="text-slate-400 hover:text-red-500 transition-colors shrink-0 disabled:opacity-40 p-1"
                      title="Delete table"
                    >
                      {deletingId === t.table_name ? (
                        <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      )}
                    </button>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <span className="text-slate-400">Rows</span>
                      <span className="font-semibold text-slate-700">{t.row_count.toLocaleString()}</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-slate-400">Columns</span>
                      <span className="font-semibold text-slate-700">{t.column_count}</span>
                    </span>
                    {t.created_at && (
                      <span className="text-slate-400">{new Date(t.created_at).toLocaleDateString()}</span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {t.columns.slice(0, 12).map((c) => (
                      <div key={c.name} className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1">
                        <span className="text-[11px] text-slate-700 font-medium">{c.name}</span>
                        <PG_BADGE type={c.pg_type} />
                      </div>
                    ))}
                    {t.columns.length > 12 && (
                      <span className="text-[11px] text-slate-400 self-center">+{t.columns.length - 12} more</span>
                    )}
                  </div>

                  <div className="pt-1 border-t border-slate-100">
                    <p className="text-xs text-slate-400">
                      Try asking: <span className="text-slate-600 italic">"Show the first 10 rows of {t.display_name}"</span>
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tips */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">Tips</p>
          <ul className="flex flex-col gap-2 text-sm text-slate-600">
            <li className="flex gap-2"><span className="text-slate-400">•</span> Column types are inferred automatically (TEXT, BIGINT, NUMERIC, TIMESTAMP, BOOLEAN)</li>
            <li className="flex gap-2"><span className="text-slate-400">•</span> The first row must be headers — QueryPilot uses them to understand your data</li>
            <li className="flex gap-2"><span className="text-slate-400">•</span> After upload, switch to the Query page and ask a natural language question about your data</li>
            <li className="flex gap-2"><span className="text-slate-400">•</span> Tables are shared across all users of this instance</li>
          </ul>
        </div>

      </div>
    </div>
  );
}
