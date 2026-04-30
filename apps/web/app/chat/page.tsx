import Link from "next/link"
import { Suspense } from "react"
import { Sparkles, ArrowLeft } from "lucide-react"
import { ChatPanel } from "@/components/chat/ChatPanel"
import { ChatPageClient } from "./ChatPageClient"

export default function ChatPage() {
  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-border px-4">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Link>
          <div className="h-4 w-px bg-border" />
          <div className="flex items-center gap-2 font-semibold text-sm">
            <Sparkles className="h-4 w-4 text-blue-500" />
            BizGrowth AI
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-border bg-muted/40 px-3 py-1 text-xs text-muted-foreground">
          <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
          Mock LLM · Ready
        </div>
      </header>

      {/* Chat area */}
      <main className="flex-1 overflow-hidden">
        <Suspense fallback={<div className="flex h-full items-center justify-center text-muted-foreground text-sm">Loading…</div>}>
          <ChatPageClient />
        </Suspense>
      </main>
    </div>
  )
}
