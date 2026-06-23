"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, BudgetPlan } from "@/lib/api";

function BudgetSection({ title, items, color, currency }: { title: string; items: Record<string, number>; color: string; currency: string }) {
  const total = Object.values(items).reduce((a, b) => a + b, 0);
  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <span className={`text-sm font-bold ${color}`}>{currency} {total.toFixed(0)}</span>
      </div>
      <div className="space-y-2">
        {Object.entries(items).filter(([,v]) => v > 0).map(([key, val]) => (
          <div key={key} className="flex items-center justify-between text-sm">
            <span className="text-gray-600 capitalize">{key.replace(/_/g, " ")}</span>
            <span className="font-medium">{currency} {val.toFixed(0)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function BudgetPage() {
  const { getToken } = useAuth();
  const [plan, setPlan] = useState<BudgetPlan | null>(null);
  const [currency, setCurrency] = useState("AED");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const token = await getToken();
        const { report } = await api.report(token!);
        setPlan(report.budget_plan);
        setCurrency(report.summary.currency);
      } catch {} finally { setLoading(false); }
    })();
  }, [getToken]);

  if (loading) return <div className="text-gray-400 text-center mt-20">Loading…</div>;
  if (!plan) return <div className="text-gray-400 text-center mt-20">Upload a statement to generate your budget plan.</div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Budget Plan</h1>
        <p className="text-gray-500 text-sm mt-1">Framework: {plan.framework}</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-green-50 rounded-2xl p-5 border border-green-100">
          <p className="text-sm text-green-700">Monthly Savings Target</p>
          <p className="text-2xl font-bold text-green-700 mt-1">{currency} {plan.monthly_target_savings?.toFixed(0)}</p>
        </div>
        <div className="bg-blue-50 rounded-2xl p-5 border border-blue-100">
          <p className="text-sm text-blue-700">Emergency Fund Goal</p>
          <p className="text-2xl font-bold text-blue-700 mt-1">{currency} {plan.emergency_fund_target?.toFixed(0)}</p>
        </div>
      </div>

      <BudgetSection title="🏠 Needs (50%)"    items={plan.recommended_budget.needs}   color="text-red-500"   currency={currency} />
      <BudgetSection title="🎮 Wants (30%)"    items={plan.recommended_budget.wants}   color="text-yellow-500" currency={currency} />
      <BudgetSection title="💰 Savings (20%)"  items={plan.recommended_budget.savings} color="text-green-600" currency={currency} />

      {plan.insights?.length > 0 && (
        <div className="bg-yellow-50 rounded-2xl p-5 border border-yellow-100">
          <h3 className="font-semibold text-yellow-800 mb-3">💡 AI Insights</h3>
          <ul className="space-y-2">
            {plan.insights.map((ins, i) => (
              <li key={i} className="text-sm text-yellow-700">• {ins}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
