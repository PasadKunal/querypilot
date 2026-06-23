export interface UserConnection {
  id: number;
  name: string;
  table_count: number;
  schema_version: string;
  created_at: string;
}

export interface QueryRequest {
  question: string;
  schema_version?: string;
  run_semantic_check?: boolean;
  connection_id?: number | null;
}

export interface QueryResponse {
  success: boolean;
  query_id: number | null;
  question: string;
  sql: string;
  rows: Record<string, unknown>[];
  row_count: number;
  columns: string[];
  truncated: boolean;
  reasoning: string;
  confidence: number;
  iterations: number;
  latency_ms: number;
  semantic_score: number | null;
  semantic_note: string | null;
  error: string | null;
  insights: string | null;
  suggested_questions: string[];
}

export interface ColumnInfo {
  name: string;
  pg_type: string;
}

export interface UserTable {
  table_name: string;
  display_name: string;
  row_count: number;
  column_count: number;
  columns: ColumnInfo[];
  created_at: string;
}

export interface SavedQuery {
  id: number;
  question: string;
  created_at: string;
}

export interface HistoryEntry {
  id: number;
  question: string;
  final_sql: string | null;
  success: boolean;
  iterations: number;
  latency_ms: number | null;
  semantic_score: number | null;
  row_count: number | null;
  created_at: string;
}
