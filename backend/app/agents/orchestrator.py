"""
Simple sequential agent orchestrator.
No LangGraph dependency — keeps it simple and free.
"""
from typing import List
from app.agents.expense_classifier   import ExpenseClassifierAgent
from app.agents.subscription_detector import SubscriptionDetectorAgent
from app.agents.waste_detector        import WasteDetectorAgent
from app.agents.budget_planner        import BudgetPlannerAgent
from app.agents.debt_optimizer        import DebtOptimizerAgent
from app.agents.savings_coach         import SavingsCoachAgent


def run_pipeline(
    transactions: List[dict],
    region: str = "UAE",
    currency: str = "AED",
) -> dict:
    """
    Full analysis pipeline. Returns complete financial report dict.
    Steps: classify → subscriptions → waste → budget → debt → savings
    """

    # 1. Classify expenses
    classifier = ExpenseClassifierAgent(region=region)
    classified = classifier.run(transactions)

    # 2. Detect subscriptions
    sub_agent = SubscriptionDetectorAgent()
    subscriptions = sub_agent.run(classified)

    # 3. Detect waste
    waste_agent = WasteDetectorAgent(currency=currency)
    waste_items = waste_agent.run(classified, subscriptions)

    # 4. Budget plan
    budget_agent = BudgetPlannerAgent(region=region, currency=currency)
    budget_plan = budget_agent.run(classified)

    # 5. Debt optimization
    debt_agent = DebtOptimizerAgent(currency=currency)
    debt_plan = debt_agent.run(classified)

    # 6. Savings coach
    savings_agent = SavingsCoachAgent(region=region, currency=currency)
    savings_plan = savings_agent.run(classified, waste_items, budget_plan)

    # 7. Summary scores
    debits  = [t for t in classified if t.get("type") == "debit"]
    credits = [t for t in classified if t.get("type") == "credit"]
    total_spend  = sum(t["amount"] for t in debits)
    total_income = sum(t["amount"] for t in credits)
    total_waste  = sum(w.get("monthly_loss", 0) for w in waste_items)

    waste_score   = max(0, 100 - min(100, int(total_waste / max(total_spend, 1) * 200)))
    savings_rate  = (total_income - total_spend) / max(total_income, 1)
    savings_score = min(100, max(0, int(savings_rate * 300)))

    # Category breakdown
    from collections import defaultdict
    cat_breakdown = defaultdict(float)
    for t in debits:
        cat_breakdown[t.get("category", "other")] += t["amount"]

    return {
        "summary": {
            "total_income":  round(total_income, 2),
            "total_spend":   round(total_spend, 2),
            "net_savings":   round(total_income - total_spend, 2),
            "waste_score":   waste_score,
            "savings_score": savings_score,
            "currency":      currency,
            "region":        region,
        },
        "category_breakdown":       {k: round(v, 2) for k, v in cat_breakdown.items()},
        "classified_transactions":  classified,
        "subscriptions":            subscriptions,
        "waste_items":              waste_items,
        "budget_plan":              budget_plan,
        "debt_plan":                debt_plan,
        "savings_plan":             savings_plan,
    }
