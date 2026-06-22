import type { HistoryEntry, QueryRequest, QueryResponse } from "./types";

const BASE_URL = "http://localhost:8000";

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("qp_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function registerUser(email: string, password: string): Promise<string> {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json() as { access_token?: string; detail?: string };
  if (!res.ok) throw new Error(data.detail ?? `Registration failed: ${res.status}`);
  return data.access_token!;
}

export async function loginUser(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  const data = await res.json() as { access_token?: string; detail?: string };
  if (!res.ok) throw new Error(data.detail ?? `Login failed: ${res.status}`);
  return data.access_token!;
}

export async function runQuery(payload: QueryRequest): Promise<QueryResponse> {
  const res = await fetch(`${BASE_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(err.detail ?? `Request failed: ${res.status}`);
  }
  return res.json() as Promise<QueryResponse>;
}

export async function fetchHistory(limit = 50): Promise<HistoryEntry[]> {
  const res = await fetch(`${BASE_URL}/api/history?limit=${limit}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`);
  return res.json() as Promise<HistoryEntry[]>;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
