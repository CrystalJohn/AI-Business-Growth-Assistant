"use client"

import { useEffect, useRef } from "react"
import { User, Sparkles } from "lucide-react"
import { ResultBlock } from "@/components/results/ResultBlock"
import { LoadingSteps } from "./LoadingSteps"
import type { ChatMessage, LoadingStep } from "@/types"

interface Props {
  messages: ChatMessage[]
  loadingStep: LoadingStep
  onFollowUp: (question: string) => void
}

export function MessageList({ messages, loadingStep, onFollowUp }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loadingStep])

  return (
    <div className="flex flex-col gap-6 px-4 py-6">
      {messages.map((msg) => (
        <div key={msg.id} className="flex flex-col gap-3">
          {/* User bubble */}
          {msg.role === "user" && (
            <div className="flex items-start justify-end gap-2.5">
              <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-2.5 text-sm text-white">
                {msg.content}
              </div>
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                <User className="h-4 w-4" />
              </div>
            </div>
          )}

          {/* AI response */}
          {msg.role === "assistant" && (
            <div className="flex items-start gap-2.5">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-500/10 text-blue-500">
                <Sparkles className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                {msg.result ? (
                  <ResultBlock result={msg.result} onFollowUp={onFollowUp} />
                ) : (
                  <p className="text-sm text-foreground">{msg.content}</p>
                )}
              </div>
            </div>
          )}
        </div>
      ))}

      {/* Inline loading indicator */}
      {loadingStep !== "idle" && loadingStep !== "done" && (
        <div className="flex items-start gap-2.5">
          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-500/10 text-blue-500">
            <Sparkles className="h-4 w-4" />
          </div>
          <div className="rounded-xl border border-border bg-card px-4 py-3">
            <LoadingSteps current={loadingStep} />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
