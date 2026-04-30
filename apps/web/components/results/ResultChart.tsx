"use client"

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import type { TableColumn } from "@/types"

const COLORS = [
  "#3b82f6", "#10b981", "#f59e0b", "#ef4444",
  "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16",
]

interface Props {
  chartType: "bar" | "line" | "area" | "pie"
  columns: TableColumn[]
  rows: Record<string, unknown>[]
}

function pickAxes(columns: TableColumn[]) {
  const xCol = columns.find((c) => c.type === "string") ?? columns[0]
  const yCol = columns.find((c) => c.type === "number")
  return { xKey: xCol?.key ?? "", yKey: yCol?.key ?? "" }
}

function formatTick(value: unknown) {
  if (typeof value === "number") {
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}k`
    return String(value)
  }
  const s = String(value)
  return s.length > 12 ? s.slice(0, 10) + "…" : s
}

export function ResultChart({ chartType, columns, rows }: Props) {
  const { xKey, yKey } = pickAxes(columns)

  if (!yKey) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
        No numeric column found for chart.
      </div>
    )
  }

  const commonProps = {
    data: rows,
    margin: { top: 8, right: 16, left: 8, bottom: 8 },
  }

  if (chartType === "pie") {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={rows}
            dataKey={yKey}
            nameKey={xKey}
            cx="50%"
            cy="50%"
            outerRadius={100}
            label={({ name, percent }) =>
              `${name} ${(percent * 100).toFixed(0)}%`
            }
          >
            {rows.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: unknown) => formatTick(v)} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === "line") {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <LineChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey={xKey} tickFormatter={formatTick} tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={formatTick} tick={{ fontSize: 12 }} width={60} />
          <Tooltip formatter={(v: unknown) => formatTick(v)} />
          <Legend />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke={COLORS[0]}
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  if (chartType === "area") {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart {...commonProps}>
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={COLORS[0]} stopOpacity={0.3} />
              <stop offset="95%" stopColor={COLORS[0]} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey={xKey} tickFormatter={formatTick} tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={formatTick} tick={{ fontSize: 12 }} width={60} />
          <Tooltip formatter={(v: unknown) => formatTick(v)} />
          <Area
            type="monotone"
            dataKey={yKey}
            stroke={COLORS[0]}
            strokeWidth={2}
            fill="url(#areaGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart {...commonProps}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis dataKey={xKey} tickFormatter={formatTick} tick={{ fontSize: 12 }} />
        <YAxis tickFormatter={formatTick} tick={{ fontSize: 12 }} width={60} />
        <Tooltip formatter={(v: unknown) => formatTick(v)} />
        <Bar dataKey={yKey} radius={[4, 4, 0, 0]}>
          {rows.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
