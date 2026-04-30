"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ResultTable } from "./ResultTable"
import { ResultChart } from "./ResultChart"
import { SqlViewer } from "./SqlViewer"
import { Sparkles, MessageSquare } from "lucide-react"
import type { QueryResponse } from "@/types"

interface Props {
  result: QueryResponse
  onFollowUp: (question: string) => void
}

export function ResultBlock({ result, onFollowUp }: Props) {
  const { answer, sql, columns, rows, chartType, followUpQuestions } = result

  const tabs = [
    { value: "answer",  label: "Answer" },
    { value: "table",   label: `Table (${rows.length})` },
    ...(chartType ? [{ value: "chart", label: "Chart" }] : []),
    { value: "sql",     label: "SQL" },
  ]

  return (
    <div className="flex flex-col gap-4 animate-fade-in">
      <Tabs defaultValue="answer">
        <TabsList className="h-9 gap-0.5">
          {tabs.map((t) => (
            <TabsTrigger key={t.value} value={t.value} className="text-xs px-3 h-7">
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* Answer */}
        <TabsContent value="answer" className="mt-3">
          <div className="flex items-start gap-2.5 rounded-xl border border-border bg-card p-4">
            <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-500">
              <Sparkles className="h-4 w-4" />
            </div>
            <p className="text-sm leading-relaxed text-foreground">{answer}</p>
          </div>
        </TabsContent>

        {/* Table */}
        <TabsContent value="table" className="mt-3">
          <ResultTable columns={columns} rows={rows} />
        </TabsContent>

        {/* Chart */}
        {chartType && (
          <TabsContent value="chart" className="mt-3">
            <div className="rounded-xl border border-border bg-card p-4">
              <ResultChart
                chartType={chartType}
                columns={columns}
                rows={rows}
              />
            </div>
          </TabsContent>
        )}

        {/* SQL */}
        <TabsContent value="sql" className="mt-3">
          <SqlViewer sql={sql} />
        </TabsContent>
      </Tabs>

      {/* Follow-up questions */}
      {followUpQuestions.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <MessageSquare className="h-3.5 w-3.5" />
            Follow-up questions
          </p>
          <div className="flex flex-wrap gap-2">
            {followUpQuestions.map((q) => (
              <button
                key={q}
                onClick={() => onFollowUp(q)}
                className="rounded-full border border-border bg-muted/40 px-3 py-1 text-xs text-muted-foreground hover:border-blue-500/50 hover:bg-blue-500/5 hover:text-foreground transition-all"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
