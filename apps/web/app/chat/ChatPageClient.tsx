"use client"

import { useSearchParams } from "next/navigation"
import { ChatPanel } from "@/components/chat/ChatPanel"

export function ChatPageClient() {
  const params = useSearchParams()
  const initialQuestion = params.get("q") ?? undefined

  return <ChatPanel initialQuestion={initialQuestion} />
}
