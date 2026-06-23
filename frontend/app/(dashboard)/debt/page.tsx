"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, DebtPlan } from "@/lib/api";

export default function DebtPage() {
  const { getToken } = useAuth();
  const [plan, setPlan] = useState<DebtPlan | null>(null);
  const [currency, setCurrency] = useState("AED");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const token = await getToken();
        const { report } = await api.report(token!);
        setPlan(report.debt_plan);
        setCurrency(report.summary.currency);
      } catch {} finally { setLoading(false); }
    })();
  }, [getToken]);

  if (loading) return <div className="text-gray-400 text-center mt-20">Loading…</div>;
  if (!plan || plan.detected_debts?.length === 0) return (
    <div className="text-center mt-20 text-gray-400">No debt detected in your statement — great news! 🎉</div>
  );

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Debt Optimizer</h1>
        <p className="text-gray-500 text-sm mt-1">Strategy: <span className="font-medium capitalize">{plan.recommended_strategy}</span></p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-red-50 rounded-2xl p-5 border border-red-100">
          <p className="text-sm text-red-700">Payoff Time</p>
          <p className="text-2xl font-bold text-red-600 mt-1">{plan.total_payoff_months} months</p>
        </div>
        <div className="bg-green-50 rounded-2xl p-5 border border-green-100">
          <p className="text-sm text-green-700">Interest Saved</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{currency} {plan.interest_saved_vs_minimum?.toFixed(0)}</p>
        </div>
      </div>

      <div className="bg-blue-50 rounded-xl p-4 text-sm text-blue-700 border border-blue-100">
        💡 {plan.strategy_reason}
      </div>

      <div className="space-y-3">
        <h2 className="font-semibold text-gray-900">Payoff Plan</h2>
        {plan.payoff_plan?.map((p, i) => (
          <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100">
            <div className="flex justify-between items-center">
              <p className="font-medium capitalize">{p.debt_type.replace(/_/g, " ")}</p>
              <span className="text-sm text-gray-500">{p.payoff_months} months</span>
            </div>
            <p className="text-sm text-red-500 mt-1">Interest: {currency} {p.total_interest?.toFixed(0)}</p>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        <h2 className="font-semibold text-gray-900">Detected Debts</h2>
        {plan.detected_debts?.map((d, i) => (
          <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100 flex justify-between items-center">
            <div>
              <p className="font-medium capitalize">{d.type.replace(/_/g, " ")}</p>
              <p className="text-sm text-gray-500">Monthly payment: {currency} {d.monthly_payment?.toFixed(0)}</p>
            </div>
            <p className="font-bold text-red-500">{currency} {d.estimated_balance?.toFixed(0)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
