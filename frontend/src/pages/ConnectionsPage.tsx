import { useCallback, useEffect, useState } from "react";
import { addConnection, deleteConnection, listConnections, refreshConnection } from "../api/client";
import type { UserConnection } from "../api/types";

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<UserConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<number | null>(null);

  const load = useCallback(async () => {
    try { setConnections(await listConnections()); }
    catch { /* silent */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !url.trim()) return;
    setError(null);
    setAdding(true);
    try {
      await addConnection(name.trim(), url.trim());
      setName("");
      setUrl("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add connection");
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id: number) => {
    setActionId(id);
    try {
      await deleteConnection(id);
      setConnections((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setActionId(null);
    }
  };

  const handleRefresh = async (id: number) => {
    setActionId(id);
    try {
      const updated = await refreshConnection(id);
      setConnections((prev) => prev.map((c) => (c.id === id ? updated : c)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Refresh failed");
    } finally {
      setActionId(null);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <div className="bg-gradient-to-b from-slate-950 to-slate-900 px-8 pt-10 pb-8 shrink-0">
        <span className="inline-flex items-center gap-1.5 bg-violet-500/15 border border-violet-500/30 text-violet-300 text-xs font-medium px-3 py-1 rounded-full mb-4">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
          Your databases
        </span>
        <h1 className="text-2xl font-bold text-white mb-1">Connect a Database</h1>
        <p className="text-slate-400 text-sm">
          Add a read-only PostgreSQL connection. QueryPilot will introspect the schema and let you query it in plain English.
        </p>
      </div>

      <div className="flex-1 bg-slate-50 px-8 py-8 flex flex-col gap-8">

        {/* Add form */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <p className="text-sm font-semibold text-slate-700 mb-4">Add new connection</p>
          <form onSubmit={handleAdd} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-slate-600">Display name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Production DB, Analytics Replica"
                className="border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-all"
                disabled={adding}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-slate-600">Connection string</label>
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="postgresql://user:password@host:5432/dbname"
                type="password"
                className="border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-all font-mono"
                disabled={adding}
              />
              <p className="text-xs text-slate-400">Use a read-only role — QueryPilot only runs SELECT queries</p>
            </div>

            {error && (
              <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
                <span className="shrink-0">✗</span>
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={adding || !name.trim() || !url.trim()}
              className="self-start flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors shadow-md shadow-violet-900/30"
            >
              {adding ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Connecting &amp; embedding schema...
                </>
              ) : (
                <> + Connect</>
              )}
            </button>
          </form>
        </div>

        {/* Connection list */}
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">
            Saved Connections {connections.length > 0 && `· ${connections.length}`}
          </p>

          {loading && (
            <div className="flex items-center gap-2 text-slate-400 text-sm py-4">
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Loading...
            </div>
          )}

          {!loading && connections.length === 0 && (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-2xl">
              <p className="text-3xl mb-3">🔌</p>
              <p className="text-slate-500 text-sm font-medium">No connections yet</p>
              <p className="text-slate-400 text-xs mt-1">Add a PostgreSQL connection above to query your own data</p>
            </div>
          )}

          <div className="flex flex-col gap-3">
            {connections.map((c) => (
              <div key={c.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-xl bg-violet-100 flex items-center justify-center text-lg shrink-0">🔌</div>
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-900 text-sm">{c.name}</p>
                    <p className="text-slate-400 text-xs mt-0.5">{c.table_count} tables · schema version {c.schema_version}</p>
                    {c.created_at && (
                      <p className="text-slate-400 text-xs">{new Date(c.created_at).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleRefresh(c.id)}
                    disabled={actionId === c.id}
                    title="Re-sync schema"
                    className="text-slate-400 hover:text-violet-600 transition-colors p-1.5 rounded-lg hover:bg-violet-50 disabled:opacity-40"
                  >
                    <svg className={`w-4 h-4 ${actionId === c.id ? "animate-spin" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(c.id)}
                    disabled={actionId === c.id}
                    title="Remove connection"
                    className="text-slate-400 hover:text-red-500 transition-colors p-1.5 rounded-lg hover:bg-red-50 disabled:opacity-40"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Info box */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">How it works</p>
          <ul className="flex flex-col gap-2 text-sm text-slate-600">
            <li className="flex gap-2"><span className="text-slate-400">1.</span> QueryPilot connects, reads your table and column names from <code className="text-xs bg-slate-100 px-1 rounded">information_schema</code></li>
            <li className="flex gap-2"><span className="text-slate-400">2.</span> Embeds the schema using Gemini so the agent understands your table structure</li>
            <li className="flex gap-2"><span className="text-slate-400">3.</span> On the Query page, select your connection from the dropdown before asking a question</li>
            <li className="flex gap-2"><span className="text-slate-400">4.</span> Only SELECT queries are allowed — your data is read-only</li>
          </ul>
        </div>

      </div>
    </div>
  );
}
