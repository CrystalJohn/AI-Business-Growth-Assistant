"use client"

import { Sparkles } from "lucide-react"

const SUGGESTIONS = [
  "What are our top 5 products by revenue?",
  "Show me monthly revenue trends for 2024.",
  "Which customer segment has the highest lifetime value?",
  "How are our marketing campaigns performing?",
  "What is our lead conversion rate by source?",
  "What is the average order value per segment?",
]

interface Props {
  onSelect: (question: string) => void
}

export function SuggestedQuestions({ onSelect }: Props) {
  return (
    <div className="flex flex-col items-center gap-6 py-8 px-4">
      <div className="text-center">
        <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-500">
          <Sparkles className="h-6 w-6" />
        </div>
        <h2 className="text-xl font-semibold text-foreground">AI Business Growth Assistant</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Ask anything about your business data in plain language.
        </p>
      </div>

      <div className="grid w-full max-w-2xl grid-cols-1 gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="group flex items-start gap-2.5 rounded-xl border border-border bg-card p-3.5 text-left text-sm text-muted-foreground transition-all hover:border-blue-500/50 hover:bg-blue-500/5 hover:text-foreground"
          >
            <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0 text-blue-400 opacity-60 group-hover:opacity-100" />
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}
