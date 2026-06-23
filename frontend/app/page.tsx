import Link from "next/link";
import { SignedIn, SignedOut } from "@clerk/nextjs";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-gray-100">
        <span className="text-xl font-bold text-green-700">💰 FinanceAI</span>
        <div className="flex gap-3">
          <SignedOut>
            <Link href="/sign-in" className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Sign In</Link>
            <Link href="/sign-up" className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700">
              Get Started Free
            </Link>
          </SignedOut>
          <SignedIn>
            <Link href="/dashboard" className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700">
              Dashboard →
            </Link>
          </SignedIn>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-8 pt-24 pb-16 text-center">
        <div className="inline-block px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full mb-6">
          🇦🇪 UAE · 🇮🇳 India · AED · INR
        </div>
        <h1 className="text-5xl font-bold text-gray-900 leading-tight mb-6">
          Your AI Personal<br />Finance Operator
        </h1>
        <p className="text-xl text-gray-500 mb-10 max-w-2xl mx-auto">
          Upload your bank statement. Get instant AI analysis — expenses categorized, subscriptions detected,
          waste identified, and a full budget + savings plan.
        </p>
        <Link href="/sign-up" className="inline-block px-8 py-4 bg-green-600 text-white text-lg font-medium rounded-xl hover:bg-green-700 transition">
          Analyze My Finances Free →
        </Link>
        <p className="mt-4 text-sm text-gray-400">No credit card · PDF, CSV, Excel supported</p>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-8 py-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        {[
          { emoji: "📊", title: "Expense Categorization", desc: "Every transaction automatically sorted into 12 categories." },
          { emoji: "🔁", title: "Subscription Detector", desc: "Never lose track of Netflix, Spotify, or any recurring charge." },
          { emoji: "🗑️", title: "Waste Detection", desc: "Find duplicate subscriptions and impulse spending patterns." },
          { emoji: "📋", title: "Budget Planner", desc: "50/30/20 budget tailored to UAE expats or India residents." },
          { emoji: "💳", title: "Debt Optimizer", desc: "Snowball vs Avalanche strategy with payoff timeline." },
          { emoji: "🌱", title: "Savings Coach", desc: "Region-specific investment tips — SIP, ETFs, FD, PPF." },
        ].map((f) => (
          <div key={f.title} className="p-6 bg-gray-50 rounded-2xl">
            <div className="text-3xl mb-3">{f.emoji}</div>
            <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
            <p className="text-sm text-gray-500">{f.desc}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
