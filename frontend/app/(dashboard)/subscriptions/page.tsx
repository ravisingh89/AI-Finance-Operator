"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, Subscription } from "@/lib/api";

const FREQ_COLOR = { monthly: "bg-blue-100 text-blue-700", quarterly: "bg-purple-100 text-purple-700", annual: "bg-orange-100 text-orange-700" };

export default function SubscriptionsPage() {
  const { getToken } = useAuth();
  const [subs, setSubs] = useState<Subscription[]>([]);
  const [currency, setCurrency] = useState("AED");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const token = await getToken();
        const { report } = await api.report(token!);
        setSubs(report.subscriptions || []);
        setCurrency(report.summary.currency);
      } catch {} finally { setLoading(false); }
    })();
  }, [getToken]);

  const monthly = subs.filter(s => s.frequency === "monthly").reduce((a, s) => a + s.amount, 0);
  const annual  = subs.reduce((a, s) => {
    const mult = s.frequency === "monthly" ? 12 : s.frequency === "quarterly" ? 4 : 1;
    return a + s.amount * mult;
  }, 0);

  if (loading) return <div className="text-gray-400 text-center mt-20">Loading…</div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Subscriptions</h1>
        <p className="text-gray-500 text-sm mt-1">Recurring charges detected in your statement</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-gray-100">
          <p className="text-sm text-gray-500">Monthly Total</p>
          <p className="text-2xl font-bold text-red-500 mt-1">{currency} {monthly.toFixed(0)}</p>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-gray-100">
          <p className="text-sm text-gray-500">Annual Total</p>
          <p className="text-2xl font-bold text-orange-500 mt-1">{currency} {annual.toFixed(0)}</p>
        </div>
      </div>

      {subs.length === 0 ? (
        <div className="bg-white rounded-2xl p-10 text-center text-gray-400 border border-gray-100">
          No subscriptions detected. Upload a statement to analyze.
        </div>
      ) : (
        <div className="space-y-3">
          {subs.map((s, i) => (
            <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100 flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">{s.merchant}</p>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium mt-1 inline-block ${FREQ_COLOR[s.frequency as keyof typeof FREQ_COLOR] || "bg-gray-100 text-gray-600"}`}>
                  {s.frequency}
                </span>
              </div>
              <div className="text-right">
                <p className="font-bold text-gray-900">{s.currency} {s.amount.toFixed(2)}</p>
                <p className="text-xs text-gray-400">{s.active ? "✅ active" : "⏸ inactive"}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
