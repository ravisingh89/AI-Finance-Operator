"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, SavingsPlan } from "@/lib/api";

const PRIORITY_COLOR = { high: "border-l-red-400", medium: "border-l-yellow-400", low: "border-l-green-400" };

export default function SavingsPage() {
  const { getToken } = useAuth();
  const [plan, setPlan] = useState<SavingsPlan | null>(null);
  const [currency, setCurrency] = useState("AED");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const token = await getToken();
        const { report } = await api.report(token!);
        setPlan(report.savings_plan);
        setCurrency(report.summary.currency);
      } catch {} finally { setLoading(false); }
    })();
  }, [getToken]);

  if (loading) return <div className="text-gray-400 text-center mt-20">Loading…</div>;
  if (!plan)   return <div className="text-gray-400 text-center mt-20">Upload a statement to get your savings plan.</div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Savings Coach</h1>
        <p className="text-gray-500 text-sm mt-1">Personalized savings and investment plan</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-gray-100">
          <p className="text-sm text-gray-500">Current Savings Rate</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{plan.current_savings_rate}%</p>
          <div className="mt-2 h-2 bg-gray-100 rounded-full">
            <div className="h-2 bg-blue-400 rounded-full" style={{ width: `${Math.min(plan.current_savings_rate, 100)}%` }} />
          </div>
        </div>
        <div className="bg-green-50 rounded-2xl p-5 border border-green-100">
          <p className="text-sm text-green-700">Projected Annual Savings</p>
          <p className="text-2xl font-bold text-green-700 mt-1">{currency} {plan.projected_annual_savings?.toFixed(0)}</p>
        </div>
      </div>

      <div>
        <h2 className="font-semibold text-gray-900 mb-3">💡 Opportunities</h2>
        <div className="space-y-3">
          {plan.opportunities?.map((op, i) => (
            <div key={i} className={`bg-white rounded-xl p-4 border-l-4 border border-gray-100 ${PRIORITY_COLOR[op.priority as keyof typeof PRIORITY_COLOR]}`}>
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium text-gray-900 text-sm">{op.description}</p>
                  <span className={`text-xs mt-1 inline-block px-2 py-0.5 rounded-full font-medium
                    ${op.priority === "high" ? "bg-red-100 text-red-700" : op.priority === "medium" ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}`}>
                    {op.priority} priority
                  </span>
                </div>
                <p className="text-green-600 font-bold text-sm">+{currency} {op.monthly_impact?.toFixed(0)}/mo</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="font-semibold text-gray-900 mb-3">📈 Investment Recommendations</h2>
        <div className="space-y-3">
          {plan.investment_recommendations?.map((inv, i) => (
            <div key={i} className="bg-white rounded-xl p-4 border border-gray-100">
              <div className="flex justify-between items-center mb-1">
                <p className="font-medium text-gray-900">{inv.product}</p>
                <span className="text-sm font-bold text-green-600">{inv.allocation_percent}%</span>
              </div>
              <p className="text-xs text-blue-600">Expected: {inv.expected_return}</p>
              <p className="text-xs text-gray-500 mt-1">{inv.rationale}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
