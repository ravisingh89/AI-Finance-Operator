"use client";
import { useReport } from "@/hooks/useReport";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { EmptyState } from "@/components/shared/EmptyState";
import { ScoreCard } from "@/components/dashboard/ScoreCard";
import { formatCurrency } from "@/lib/utils";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from "recharts";
import Link from "next/link";

const COLORS = ["#22c55e","#3b82f6","#f59e0b","#ef4444","#8b5cf6","#ec4899","#14b8a6","#f97316","#6366f1","#84cc16"];

export default function Dashboard() {
  const { report, loading, error } = useReport();

  if (loading) return <LoadingSpinner text="Loading your financial report…" />;
  if (error || !report) return <EmptyState />;

  const { summary, category_breakdown } = report;
  const cur = summary.currency;

  const pieData = Object.entries(category_breakdown)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, value]) => ({ name, value: Math.round(value) }));

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">{summary.region} · {cur} · Your latest statement</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Income",  value: formatCurrency(summary.total_income, cur), color: "text-green-600" },
          { label: "Total Spend",   value: formatCurrency(summary.total_spend,  cur), color: "text-red-500"   },
          { label: "Net Savings",   value: formatCurrency(summary.net_savings,  cur), color: "text-blue-600"  },
          { label: "Subscriptions", value: `${report.subscriptions?.length ?? 0} found`, color: "text-purple-600" },
        ].map(c => (
          <div key={c.label} className="bg-white rounded-2xl p-5 border border-gray-100">
            <p className="text-sm text-gray-500">{c.label}</p>
            <p className={`text-xl font-bold mt-1 ${c.color}`}>{c.value}</p>
          </div>
        ))}
      </div>

      {/* Scores */}
      <div className="grid grid-cols-2 gap-4">
        <ScoreCard label="Savings Score" score={summary.savings_score} color="#22c55e" />
        <ScoreCard label="Waste Score"   score={summary.waste_score}   color="#f59e0b" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-gray-100">
          <h2 className="font-semibold text-gray-900 mb-4">Spend by Category</h2>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={85} label={({ name }) => name}>
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v: number) => formatCurrency(v, cur)} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-gray-100">
          <h2 className="font-semibold text-gray-900 mb-4">Category Breakdown</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={pieData} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" width={95} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatCurrency(v, cur)} />
              <Bar dataKey="value" fill="#22c55e" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { href: "/subscriptions", label: "Subscriptions", icon: "🔁" },
          { href: "/budget",        label: "Budget Plan",   icon: "📋" },
          { href: "/debt",          label: "Debt Planner",  icon: "💳" },
          { href: "/savings",       label: "Savings Coach", icon: "🌱" },
        ].map(l => (
          <Link key={l.href} href={l.href}
            className="flex items-center gap-2 p-4 bg-white border border-gray-100 rounded-xl hover:border-green-300 transition text-sm font-medium">
            <span>{l.icon}</span>{l.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
