import type { QueryResponse } from "@/types"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export async function postQuery(question: string): Promise<QueryResponse> {
  return request<QueryResponse>("/chat/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  })
}

export async function validateSQL(sql: string) {
  return request<{ valid: boolean; error?: string; formatted?: string }>(
    "/sql/validate",
    { method: "POST", body: JSON.stringify({ sql }) }
  )
}

export async function getSchema() {
  return request<{ tables: unknown[] }>("/schema")
}

export async function healthCheck() {
  return request<{ status: string }>("/health")
}
