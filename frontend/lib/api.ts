const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function req<T>(path: string, token: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API ${res.status}: ${err}`);
  }
  return res.json();
}

export const api = {
  async upload(file: File, currency: string, region: string, token: string) {
    const form = new FormData();
    form.append("file", file);
    form.append("currency", currency);
    form.append("region", region);
    return req<{ statement_id: string; status: string }>(
      "/api/v1/statements/upload", token, { method: "POST", body: form }
    );
  },

  status: (id: string, token: string) =>
    req<{ status: string }>(`/api/v1/statements/${id}/status`, token),

  report: (token: string) =>
    req<{ report: FinancialReport }>("/api/v1/reports/latest", token),

  transactions: (token: string) =>
    req<{ transactions: Transaction[] }>("/api/v1/transactions", token),
};

// ─── Types ──────────────────────────────────────────────────────────────────

export interface FinancialReport {
  summary: {
    total_income: number;
    total_spend: number;
    net_savings: number;
    waste_score: number;
    savings_score: number;
    currency: string;
    region: string;
  };
  category_breakdown: Record<string, number>;
  subscriptions: Subscription[];
  waste_items: WasteItem[];
  budget_plan: BudgetPlan;
  debt_plan: DebtPlan;
  savings_plan: SavingsPlan;
  classified_transactions: Transaction[];
}

export interface Transaction {
  date: string;
  merchant: string;
  amount: number;
  currency: string;
  type: string;
  category: string;
}

export interface Subscription {
  merchant: string;
  frequency: string;
  amount: number;
  currency: string;
  active: boolean;
}

export interface WasteItem {
  waste_type: string;
  merchant: string;
  severity: "low" | "medium" | "high";
  monthly_loss: number;
  recommendation: string;
}

export interface BudgetPlan {
  framework: string;
  recommended_budget: {
    needs: Record<string, number>;
    wants: Record<string, number>;
    savings: Record<string, number>;
  };
  monthly_target_savings: number;
  emergency_fund_target: number;
  insights: string[];
}

export interface DebtPlan {
  recommended_strategy: string;
  strategy_reason: string;
  detected_debts: Array<{ type: string; estimated_balance: number; monthly_payment: number }>;
  payoff_plan: Array<{ debt_type: string; payoff_months: number; total_interest: number }>;
  interest_saved_vs_minimum: number;
  total_payoff_months: number;
}

export interface SavingsPlan {
  current_savings_rate: number;
  target_savings_rate: number;
  opportunities: Array<{ type: string; description: string; monthly_impact: number; priority: string }>;
  investment_recommendations: Array<{ product: string; allocation_percent: number; expected_return: string; rationale: string }>;
  projected_annual_savings: number;
}
