import type { HistoryEntry, QueryRequest, QueryResponse, SavedQuery, UserConnection, UserTable } from "./types";

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

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

export async function uploadCSV(file: File): Promise<UserTable> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/api/tables/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(err.detail ?? `Upload failed: ${res.status}`);
  }
  return res.json() as Promise<UserTable>;
}

export async function listUserTables(): Promise<UserTable[]> {
  const res = await fetch(`${BASE_URL}/api/tables`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Failed to load tables: ${res.status}`);
  return res.json() as Promise<UserTable[]>;
}

export async function deleteUserTable(tableName: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/tables/${tableName}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to delete table: ${res.status}`);
}

export async function listConnections(): Promise<UserConnection[]> {
  const res = await fetch(`${BASE_URL}/api/connections`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Failed to load connections: ${res.status}`);
  return res.json() as Promise<UserConnection[]>;
}

export async function addConnection(name: string, connection_url: string): Promise<UserConnection> {
  const res = await fetch(`${BASE_URL}/api/connections`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ name, connection_url }),
  });
  const data = await res.json() as UserConnection & { detail?: string };
  if (!res.ok) throw new Error((data as { detail?: string }).detail ?? `Failed: ${res.status}`);
  return data;
}

export async function deleteConnection(id: number): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/connections/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to delete connection: ${res.status}`);
}

export async function refreshConnection(id: number): Promise<UserConnection> {
  const res = await fetch(`${BASE_URL}/api/connections/${id}/refresh`, {
    method: "POST",
    headers: authHeaders(),
  });
  const data = await res.json() as UserConnection & { detail?: string };
  if (!res.ok) throw new Error((data as { detail?: string }).detail ?? `Failed: ${res.status}`);
  return data;
}

export async function submitFeedback(queryId: number, rating: 1 | 5): Promise<void> {
  await fetch(`${BASE_URL}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ query_id: queryId, rating }),
  });
}

export async function listSavedQueries(): Promise<SavedQuery[]> {
  const res = await fetch(`${BASE_URL}/api/saved`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json() as Promise<SavedQuery[]>;
}

export async function saveQuery(question: string): Promise<SavedQuery> {
  const res = await fetch(`${BASE_URL}/api/saved`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json() as Promise<SavedQuery>;
}

export async function deleteSavedQuery(id: number): Promise<void> {
  await fetch(`${BASE_URL}/api/saved/${id}`, { method: "DELETE", headers: authHeaders() });
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
