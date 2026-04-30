"use client"

import { Check, Loader2 } from "lucide-react"
import type { LoadingStep } from "@/types"

const STEPS: { id: LoadingStep; label: string }[] = [
  { id: "understanding", label: "Understanding your question" },
  { id: "generating",    label: "Generating SQL query" },
  { id: "executing",     label: "Executing against database" },
  { id: "formatting",    label: "Formatting results" },
]

const ORDER: LoadingStep[] = ["understanding", "generating", "executing", "formatting", "done"]

function stepIndex(step: LoadingStep) {
  return ORDER.indexOf(step)
}

interface Props {
  current: LoadingStep
}

export function LoadingSteps({ current }: Props) {
  const currentIdx = stepIndex(current)

  return (
    <div className="flex flex-col gap-2 py-2">
      {STEPS.map(({ id, label }) => {
        const idx = stepIndex(id)
        const done = currentIdx > idx
        const active = currentIdx === idx

        return (
          <div key={id} className="flex items-center gap-3 text-sm">
            <div
              className={[
                "flex h-5 w-5 items-center justify-center rounded-full border transition-all",
                done   ? "border-green-500 bg-green-500 text-white" : "",
                active ? "border-blue-500 bg-blue-500/10 text-blue-500" : "",
                !done && !active ? "border-muted-foreground/30 text-muted-foreground/30" : "",
              ].join(" ")}
            >
              {done ? (
                <Check className="h-3 w-3" />
              ) : active ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <span className="h-1.5 w-1.5 rounded-full bg-current" />
              )}
            </div>
            <span
              className={[
                "transition-colors",
                done   ? "text-green-600 dark:text-green-400" : "",
                active ? "text-foreground font-medium" : "",
                !done && !active ? "text-muted-foreground/50" : "",
              ].join(" ")}
            >
              {label}
              {active && <span className="ml-1 animate-pulse">…</span>}
            </span>
          </div>
        )
      })}
    </div>
  )
}
