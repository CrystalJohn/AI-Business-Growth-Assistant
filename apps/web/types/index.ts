export interface TableColumn {
  key: string
  label: string
  type: "string" | "number" | "date"
}

export interface QueryResponse {
  answer: string
  sql: string
  columns: TableColumn[]
  rows: Record<string, unknown>[]
  chartType?: "bar" | "line" | "pie" | "area" | null
  followUpQuestions: string[]
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  result?: QueryResponse
  timestamp: Date
}

export type LoadingStep =
  | "idle"
  | "understanding"
  | "generating"
  | "executing"
  | "formatting"
  | "done"
