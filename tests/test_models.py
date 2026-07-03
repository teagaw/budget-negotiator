# tests/test_models.py
from src.models import Transaction, CategorizedTransactions, BudgetPlan


def test_transaction_creation():
    t = Transaction(amount=45.50, category="food", description="Grocery store")
    assert t.amount == 45.50
    assert t.category == "food"
    assert t.description == "Grocery store"


def test_categorized_transactions_creation():
    cats = CategorizedTransactions(
        essential={"rent": 1200, "utilities": 150},
        discretionary={"entertainment": 80, "dining": 120},
        total=1550
    )
    assert cats.essential["rent"] == 1200
    assert cats.total == 1550


def test_budget_plan_creation():
    plan = BudgetPlan(
        original_spending=1550,
        proposed_spending=1300,
        savings=250,
        cuts={"entertainment": 60, "dining": 40},
        explanation="Cut discretionary spending by 50%"
    )
    assert plan.savings == 250
    assert plan.cuts["entertainment"] == 60