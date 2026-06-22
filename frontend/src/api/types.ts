export interface QueryRequest {
  question: string;
  schema_version?: string;
  run_semantic_check?: boolean;
}

export interface QueryResponse {
  success: boolean;
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
