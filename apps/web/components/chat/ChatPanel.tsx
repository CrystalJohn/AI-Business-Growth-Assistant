"use client"

import { useState, useCallback } from "react"
import { MessageList } from "./MessageList"
import { QuestionInput } from "./QuestionInput"
import { SuggestedQuestions } from "./SuggestedQuestions"
import { postQuery } from "@/lib/api"
import type { ChatMessage, LoadingStep } from "@/types"

const STEP_DELAYS: [LoadingStep, number][] = [
  ["understanding", 400],
  ["generating",    900],
  ["executing",     1500],
  ["formatting",    2100],
]

interface Props {
  initialQuestion?: string
}

export function ChatPanel({ initialQuestion }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loadingStep, setLoadingStep] = useState<LoadingStep>("idle")
  const [pendingQuestion, setPendingQuestion] = useState(initialQuestion ?? "")

  const handleSubmit = useCallback(async (question: string) => {
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setPendingQuestion("")

    // Animate loading steps
    setLoadingStep("understanding")
    for (const [step, delay] of STEP_DELAYS) {
      await new Promise((r) => setTimeout(r, delay - (STEP_DELAYS[0][1])))
      setLoadingStep(step)
    }
    await new Promise((r) => setTimeout(r, 500))

    try {
      const result = await postQuery(question)
      setLoadingStep("done")

      const aiMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: result.answer,
        result,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `Error: ${err instanceof Error ? err.message : "Something went wrong. Is the API running?"}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoadingStep("idle")
    }
  }, [])

  const isEmpty = messages.length === 0 && loadingStep === "idle"

  return (
    <div className="flex h-full flex-col">
      {/* Message area */}
      <div className="flex-1 overflow-y-auto">
        {isEmpty ? (
          <SuggestedQuestions onSelect={handleSubmit} />
        ) : (
          <div className="mx-auto max-w-3xl">
            <MessageList
              messages={messages}
              loadingStep={loadingStep}
              onFollowUp={handleSubmit}
            />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="mx-auto w-full max-w-3xl">
        <QuestionInput
          onSubmit={handleSubmit}
          loading={loadingStep !== "idle"}
          initialValue={pendingQuestion}
        />
      </div>
    </div>
  )
}
