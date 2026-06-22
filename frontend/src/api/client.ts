import type { HistoryEntry, QueryRequest, QueryResponse } from "./types";

const BASE_URL = "http://localhost:8000";

export async function runQuery(payload: QueryRequest): Promise<QueryResponse> {
  const res = await fetch(`${BASE_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchHistory(limit = 50): Promise<HistoryEntry[]> {
  const res = await fetch(`${BASE_URL}/api/history?limit=${limit}`);
  if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`);
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
