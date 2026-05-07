export interface QueryResponse {
  answer: string
  data: Record<string, unknown>[] | Record<string, unknown>
  rows: number
  tool: string | null
  chart_type?: "bar" | "line" | "pie" | "area" | null
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
