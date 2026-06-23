from typing import List
from collections import defaultdict

class DebtOptimizerAgent:
    UAE_CARD_RATE = 0.36   # 36% APR typical UAE credit card
    IND_CARD_RATE = 0.42   # 42% APR typical India credit card
    EMI_RATE      = 0.14   # ~14% personal loans

    def __init__(self, currency: str = "AED"):
        self.currency = currency
        self.card_rate = self.UAE_CARD_RATE if currency == "AED" else self.IND_CARD_RATE

    def run(self, transactions: List[dict]) -> dict:
        debt_txs = [t for t in transactions if t.get("category") == "debt" and t.get("type") == "debit"]

        if not debt_txs:
            return {"message": "No debt transactions detected.", "detected_debts": [],
                    "recommended_strategy": "none", "interest_saved_vs_minimum": 0, "total_payoff_months": 0}

        # Estimate debts from monthly payments
        monthly_debt = defaultdict(float)
        for t in debt_txs:
            m = t.get("merchant", "debt").lower()
            key = "credit_card" if any(k in m for k in ["card", "visa", "mastercard", "amex"]) else "loan"
            monthly_debt[key] += t["amount"]

        detected_debts = []
        for dtype, monthly_pay in monthly_debt.items():
            rate = self.card_rate if dtype == "credit_card" else self.EMI_RATE
            estimated_balance = monthly_pay * 24  # rough 2yr estimate
            detected_debts.append({
                "type":              dtype,
                "estimated_balance": round(estimated_balance, 2),
                "interest_rate":     rate,
                "monthly_payment":   round(monthly_pay, 2),
            })

        # Avalanche strategy (highest rate first — mathematically best)
        sorted_debts = sorted(detected_debts, key=lambda d: d["interest_rate"], reverse=True)

        payoff_plan = []
        total_interest = 0
        for d in sorted_debts:
            months, interest = self._payoff_months(d["estimated_balance"], d["monthly_payment"], d["interest_rate"])
            payoff_plan.append({
                "debt_type":      d["type"],
                "payoff_months":  months,
                "total_interest": round(interest, 2),
            })
            total_interest += interest

        # Minimum payment comparison
        min_interest = sum(
            self._payoff_months(d["estimated_balance"], d["monthly_payment"] * 0.5, d["interest_rate"])[1]
            for d in detected_debts
        )

        return {
            "detected_debts":            detected_debts,
            "recommended_strategy":      "avalanche",
            "strategy_reason":           "Avalanche pays highest-interest debt first, saving most money overall.",
            "payoff_plan":               payoff_plan,
            "interest_saved_vs_minimum": round(min_interest - total_interest, 2),
            "total_payoff_months":       max((p["payoff_months"] for p in payoff_plan), default=0),
        }

    def _payoff_months(self, balance: float, monthly: float, annual_rate: float):
        if monthly <= 0 or balance <= 0:
            return 0, 0
        monthly_rate = annual_rate / 12
        if monthly <= balance * monthly_rate:
            # Payment doesn't cover interest — cap at 120 months
            return 120, balance * annual_rate * 10
        months = 0
        total_interest = 0
        remaining = balance
        while remaining > 0 and months < 360:
            interest = remaining * monthly_rate
            total_interest += interest
            remaining = remaining + interest - monthly
            months += 1
        return months, total_interest
