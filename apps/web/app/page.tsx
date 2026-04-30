import Link from "next/link"
import {
  BarChart3,
  MessageSquare,
  Table2,
  Zap,
  TrendingUp,
  Database,
  ArrowRight,
  Sparkles,
} from "lucide-react"

const FEATURES = [
  {
    icon: MessageSquare,
    title: "Natural Language Queries",
    description:
      "Ask questions in plain English. No SQL knowledge required.",
  },
  {
    icon: BarChart3,
    title: "Instant Charts",
    description:
      "Automatically generates bar, line, and pie charts from your data.",
  },
  {
    icon: Table2,
    title: "Interactive Tables",
    description:
      "Sortable, paginated result tables powered by TanStack Table.",
  },
  {
    icon: Database,
    title: "SQL Transparency",
    description:
      "See the exact SQL query generated — copy, audit, or modify it.",
  },
  {
    icon: TrendingUp,
    title: "Business Insights",
    description:
      "Revenue trends, customer segments, campaign ROI and more.",
  },
  {
    icon: Zap,
    title: "Plug-in LLM",
    description:
      "Mock provider out of the box. Swap in Gemini or Groq with one env var.",
  },
]

const SAMPLE_QUESTIONS = [
  "What are our top 5 products by revenue?",
  "Show me monthly revenue trends for 2024.",
  "Which customer segment has the highest lifetime value?",
  "How are our marketing campaigns performing?",
  "What is our lead conversion rate by source?",
  "What is the average order value per segment?",
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Nav */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50 bg-slate-950/80">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-2 font-bold text-lg">
            <Sparkles className="h-5 w-5 text-blue-400" />
            <span>BizGrowth AI</span>
          </div>
          <nav className="flex items-center gap-6 text-sm text-slate-400">
            <Link href="#features" className="hover:text-white transition-colors">
              Features
            </Link>
            <Link href="#questions" className="hover:text-white transition-colors">
              Examples
            </Link>
            <Link
              href="/chat"
              className="rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors px-4 py-1.5 text-white font-medium"
            >
              Open Chat
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-6 pt-28 pb-20 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300 mb-8">
          <Sparkles className="h-3.5 w-3.5" />
          No SQL required · No paid API key needed
        </div>

        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-white via-blue-100 to-blue-400 bg-clip-text text-transparent">
          Ask your business data
          <br />
          anything.
        </h1>

        <p className="max-w-2xl mx-auto text-lg text-slate-400 mb-10">
          An AI-powered ChatBI assistant that translates plain-language questions
          into SQL queries, interactive tables, and beautiful charts — instantly.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 transition-colors px-8 py-3.5 text-white font-semibold text-base shadow-lg shadow-blue-500/25"
          >
            Start Chatting
            <ArrowRight className="h-4 w-4" />
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-xl border border-white/20 hover:border-white/40 transition-colors px-8 py-3.5 text-slate-300 hover:text-white font-semibold text-base"
          >
            API Docs
          </a>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Everything you need for data-driven decisions
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-2xl border border-white/10 bg-white/5 p-6 hover:border-blue-500/40 hover:bg-white/8 transition-all"
            >
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/15 text-blue-400">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-white mb-2">{title}</h3>
              <p className="text-sm text-slate-400">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Sample Questions */}
      <section id="questions" className="container mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-center mb-4">
          Try these questions
        </h2>
        <p className="text-center text-slate-400 mb-12">
          Click any question to jump straight into the chat.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto">
          {SAMPLE_QUESTIONS.map((q) => (
            <Link
              key={q}
              href={`/chat?q=${encodeURIComponent(q)}`}
              className="group flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-4 hover:border-blue-500/50 hover:bg-blue-500/10 transition-all text-sm text-slate-300 hover:text-white"
            >
              <MessageSquare className="h-4 w-4 mt-0.5 shrink-0 text-blue-400 group-hover:text-blue-300" />
              {q}
            </Link>
          ))}
        </div>
      </section>

      {/* CTA Banner */}
      <section className="container mx-auto px-6 py-20">
        <div className="rounded-2xl border border-blue-500/30 bg-gradient-to-r from-blue-950 to-slate-900 p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to explore your data?</h2>
          <p className="text-slate-400 mb-8">
            No configuration needed. The mock LLM is running and the demo database is seeded.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 transition-colors px-8 py-3.5 text-white font-semibold"
          >
            Open Chat Assistant
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="container mx-auto px-6 text-center text-sm text-slate-500">
          AI Business Growth Assistant · Boilerplate v0.1 · LLM: Mock
        </div>
      </footer>
    </div>
  )
}
