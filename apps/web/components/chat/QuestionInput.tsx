"use client"

import { useRef, useState, useEffect } from "react"
import { Send, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Props {
  onSubmit: (question: string) => void
  loading: boolean
  initialValue?: string
}

export function QuestionInput({ onSubmit, loading, initialValue = "" }: Props) {
  const [value, setValue] = useState(initialValue)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (initialValue) {
      setValue(initialValue)
    }
  }, [initialValue])

  function autoResize() {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = Math.min(el.scrollHeight, 160) + "px"
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  function handleSubmit() {
    const q = value.trim()
    if (!q || loading) return
    onSubmit(q)
    setValue("")
    if (textareaRef.current) textareaRef.current.style.height = "auto"
  }

  return (
    <div className="border-t border-border bg-background/95 backdrop-blur px-4 py-3">
      <div className="mx-auto flex max-w-3xl items-end gap-3 rounded-xl border border-border bg-card px-4 py-2.5 shadow-sm focus-within:border-blue-500/60 focus-within:ring-1 focus-within:ring-blue-500/20 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          disabled={loading}
          placeholder="Ask a question about your business data…"
          className="flex-1 resize-none bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none disabled:opacity-50"
          onChange={(e) => { setValue(e.target.value); autoResize() }}
          onKeyDown={handleKeyDown}
        />
        <Button
          size="icon"
          disabled={!value.trim() || loading}
          onClick={handleSubmit}
          className="h-8 w-8 shrink-0 rounded-lg"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
      <p className="mt-1.5 text-center text-xs text-muted-foreground">
        Press <kbd className="rounded border border-border px-1 font-mono text-[10px]">Enter</kbd> to send · <kbd className="rounded border border-border px-1 font-mono text-[10px]">Shift+Enter</kbd> for newline
      </p>
    </div>
  )
}
