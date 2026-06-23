"use client";
import { useReport } from "@/hooks/useReport";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { EmptyState } from "@/components/shared/EmptyState";
import { formatCurrency } from "@/lib/utils";
import { useState } from "react";

const CAT_COLORS: Record<string, string> = {
  groceries:     "bg-green-100 text-green-700",
  transport:     "bg-blue-100 text-blue-700",
  dining:        "bg-orange-100 text-orange-700",
  subscriptions: "bg-purple-100 text-purple-700",
  shopping:      "bg-pink-100 text-pink-700",
  rent:          "bg-red-100 text-red-700",
  salary:        "bg-emerald-100 text-emerald-700",
  utilities:     "bg-yellow-100 text-yellow-700",
  debt:          "bg-red-100 text-red-700",
  investments:   "bg-indigo-100 text-indigo-700",
  healthcare:    "bg-teal-100 text-teal-700",
  entertainment: "bg-fuchsia-100 text-fuchsia-700",
  other:         "bg-gray-100 text-gray-600",
};

export default function InsightsPage() {
  const { report, loading, error } = useReport();
  const [filter, setFilter] = useState("all");

  if (loading) return <LoadingSpinner text="Loading transactions…" />;
  if (error || !report) return <EmptyState />;

  const txs = report.classified_transactions || [];
  const cur = report.summary.currency;
  const categories = ["all", ...Array.from(new Set(txs.map(t => t.category).filter(Boolean)))];
  const filtered = filter === "all" ? txs : txs.filter(t => t.category === filter);

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Insights & Transactions</h1>
        <p className="text-sm text-gray-500 mt-1">{txs.length} transactions analysed</p>
      </div>

      {report.waste_items?.length > 0 && (
        <div className="bg-red-50 border border-red-100 rounded-2xl p-5">
          <p className="font-semibold text-red-700 mb-3">🗑️ Waste Detected</p>
          <div className="space-y-2">
            {report.waste_items.map((w, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-gray-700">{w.recommendation}</span>
                <span className="font-medium text-red-600">-{formatCurrency(w.monthly_loss, cur)}/mo</span>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-red-500">
            Total waste: {formatCurrency(report.waste_items.reduce((a, w) => a + w.monthly_loss, 0), cur)}/mo
          </p>
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        {categories.map(cat => (
          <button key={cat} onClick={() => setFilter(cat)}
            className={`px-3 py-1 rounded-full text-xs font-medium capitalize transition
              ${filter === cat ? "bg-green-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
            {cat}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {filtered.slice(0, 100).map((tx, i) => (
          <div key={i} className="bg-white rounded-xl px-4 py-3 border border-gray-100 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-900">{tx.merchant || "Unknown"}</p>
              <p className="text-xs text-gray-400">{tx.date}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${CAT_COLORS[tx.category] || CAT_COLORS.other}`}>
                {tx.category || "other"}
              </span>
              <p className={`text-sm font-bold ${tx.type === "credit" ? "text-green-600" : "text-gray-900"}`}>
                {tx.type === "credit" ? "+" : "-"}{formatCurrency(tx.amount, tx.currency || cur)}
              </p>
            </div>
          </div>
        ))}
        {filtered.length > 100 && (
          <p className="text-center text-xs text-gray-400 pt-2">Showing first 100 of {filtered.length}</p>
        )}
      </div>
    </div>
  );
}
