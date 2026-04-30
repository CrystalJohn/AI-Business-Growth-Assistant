"use client"

import { useState } from "react"
import { Copy, Check, Code2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Props {
  sql: string
}

export function SqlViewer({ sql }: Props) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    await navigator.clipboard.writeText(sql)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const highlighted = sql
    .replace(
      /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|GROUP BY|ORDER BY|HAVING|LIMIT|OFFSET|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|AS|AND|OR|NOT|IN|IS|NULL|DISTINCT|COUNT|SUM|AVG|MIN|MAX|ROUND|COALESCE|CASE|WHEN|THEN|ELSE|END|WITH|UNION|ALL|ASC|DESC|BY|INTO|VALUES|SET)\b/gi,
      (match) => `<span class="text-blue-400 font-semibold">${match}</span>`
    )
    .replace(
      /'[^']*'/g,
      (match) => `<span class="text-green-400">${match}</span>`
    )
    .replace(
      /--[^\n]*/g,
      (match) => `<span class="text-slate-500 italic">${match}</span>`
    )
    .replace(
      /\b(\d+(\.\d+)?)\b/g,
      (match) => `<span class="text-amber-400">${match}</span>`
    )

  return (
    <div className="relative rounded-lg border border-border bg-slate-950 overflow-hidden">
      <div className="flex items-center justify-between border-b border-border/50 px-4 py-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Code2 className="h-3.5 w-3.5" />
          <span>Generated SQL</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 gap-1.5 text-xs"
          onClick={handleCopy}
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-green-500" />
              Copied
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              Copy
            </>
          )}
        </Button>
      </div>
      <pre className="overflow-x-auto p-4 text-sm leading-relaxed text-slate-300 font-mono">
        <code dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </div>
  )
}
