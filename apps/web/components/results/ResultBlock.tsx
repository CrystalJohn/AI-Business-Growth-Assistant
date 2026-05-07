"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ResultTable } from "./ResultTable"
import { ResultChart } from "./ResultChart"
import { Sparkles } from "lucide-react"
import type { QueryResponse } from "@/types"

interface Props {
  result: QueryResponse
  onFollowUp: (question: string) => void
}

export function ResultBlock({ result, onFollowUp }: Props) {
  const { answer, data, rows, tool, chart_type } = result

  const dataArray = Array.isArray(data) ? data : data ? [data] : []
  const columns = dataArray.length > 0
    ? Object.keys(dataArray[0]).map((key) => ({
        key,
        label: key,
        type: typeof dataArray[0][key] === "number" ? "number" as const : "string" as const,
      }))
    : []

  const tabs = [
    { value: "answer", label: "Answer" },
    ...(dataArray.length > 0 ? [{ value: "table", label: `Table (${rows})` }] : []),
    ...(chart_type && dataArray.length > 0 ? [{ value: "chart", label: "Chart" }] : []),
  ]

  return (
    <div className="flex flex-col gap-4 animate-fade-in">
      {tool && (
        <div className="inline-flex items-center gap-1.5 self-start rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs text-blue-400">
          <Sparkles className="h-3 w-3" />
          {tool}
        </div>
      )}

      <Tabs defaultValue="answer">
        <TabsList className="h-9 gap-0.5">
          {tabs.map((t) => (
            <TabsTrigger key={t.value} value={t.value} className="text-xs px-3 h-7">
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="answer" className="mt-3">
          <div className="flex items-start gap-2.5 rounded-xl border border-border bg-card p-4">
            <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-500">
              <Sparkles className="h-4 w-4" />
            </div>
            <p className="text-sm leading-relaxed text-foreground">{answer}</p>
          </div>
        </TabsContent>

        {dataArray.length > 0 && (
          <TabsContent value="table" className="mt-3">
            <ResultTable columns={columns} rows={dataArray} />
          </TabsContent>
        )}

        {chart_type && dataArray.length > 0 && (
          <TabsContent value="chart" className="mt-3">
            <div className="rounded-xl border border-border bg-card p-4">
              <ResultChart chartType={chart_type} columns={columns} rows={dataArray} />
            </div>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
