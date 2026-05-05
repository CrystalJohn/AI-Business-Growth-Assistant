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
    title: "Truy vấn tự nhiên",
    description:
      "Hỏi về nhân sự, lương, chấm công bằng tiếng Việt. Không cần biết SQL.",
  },
  {
    icon: BarChart3,
    title: "Biểu đồ tức thì",
    description:
      "Tự động sinh bar/line/pie từ kết quả truy vấn HR.",
  },
  {
    icon: Table2,
    title: "Bảng tương tác",
    description:
      "Bảng sắp xếp + phân trang bằng TanStack Table.",
  },
  {
    icon: Database,
    title: "SQL minh bạch",
    description:
      "Xem SQL sinh ra, copy/audit; readonly role chặn ghi dữ liệu.",
  },
  {
    icon: TrendingUp,
    title: "Bảo mật PII",
    description:
      "Row-Level Security + mask lương/CCCD cho HR Viewer; audit mọi câu hỏi.",
  },
  {
    icon: Zap,
    title: "LLM cắm-chạy",
    description:
      "Mock LLM mặc định. Đổi Gemini/Groq bằng 1 env var.",
  },
]

const SAMPLE_QUESTIONS = [
  "Headcount theo phòng ban?",
  "Ai có sinh nhật trong tháng này?",
  "Lương trung bình theo cấp bậc?",
  "Ai chưa duyệt nghỉ phép tuần này?",
  "Top 10 đánh giá xuất sắc 2024-H2?",
  "Phân bố thâm niên nhân viên?",
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Nav */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50 bg-slate-950/80">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-2 font-bold text-lg">
            <Sparkles className="h-5 w-5 text-blue-400" />
            <span>HR ChatBI</span>
          </div>
          <nav className="flex items-center gap-6 text-sm text-slate-400">
            <Link href="#features" className="hover:text-white transition-colors">
              Tính năng
            </Link>
            <Link href="#questions" className="hover:text-white transition-colors">
              Ví dụ
            </Link>
            <Link
              href="/chat"
              className="rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors px-4 py-1.5 text-white font-medium"
            >
              Mở Chat
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-6 pt-28 pb-20 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300 mb-8">
          <Sparkles className="h-3.5 w-3.5" />
          Không cần SQL · Không cần API key trả phí
        </div>

        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-white via-blue-100 to-blue-400 bg-clip-text text-transparent">
          Hỏi dữ liệu nhân sự
          <br />
          bằng tiếng Việt.
        </h1>

        <p className="max-w-2xl mx-auto text-lg text-slate-400 mb-10">
          Trợ lý AI dịch câu hỏi tự nhiên thành SQL an toàn, bảng và biểu đồ
          — bảo mật theo vai trò (RBAC + RLS), che PII tự động.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 transition-colors px-8 py-3.5 text-white font-semibold text-base shadow-lg shadow-blue-500/25"
          >
            Bắt đầu chat
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
          Đầy đủ tính năng cho quyết định dựa trên dữ liệu
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
          Thử các câu hỏi sau
        </h2>
        <p className="text-center text-slate-400 mb-12">
          Bấm vào câu hỏi bất kỳ để vào thẳng chat.
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
          <h2 className="text-3xl font-bold mb-4">Sẵn sàng khám phá dữ liệu nhân sự?</h2>
          <p className="text-slate-400 mb-8">
            Không cần cấu hình. Mock LLM đang chạy, database HR demo đã được seed.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 transition-colors px-8 py-3.5 text-white font-semibold"
          >
            Mở Chat Assistant
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="container mx-auto px-6 text-center text-sm text-slate-500">
          HR ChatBI Assistant · Boilerplate v0.1 · LLM: Mock
        </div>
      </footer>
    </div>
  )
}
