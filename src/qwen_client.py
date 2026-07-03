# src/qwen_client.py
import os
import json
import dashscope
from dashscope import Generation
from src.models import CategorizedTransactions, BudgetPlan

# Load API key from environment
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


def build_prompt(categorized: CategorizedTransactions, savings_goal) -> str:
    """Build the initial negotiation prompt for Qwen."""
    goal_text = (
        f"The user wants to save ${savings_goal} per month."
        if savings_goal != "auto"
        else "The user wants to save as much as possible without hurting essentials."
    )

    prompt = f"""You are a budget negotiator. Analyze this spending and propose cuts.

MONTHLY SPENDING:
Essential: {json.dumps(categorized.essential, indent=2)}
Discretionary: {json.dumps(categorized.discretionary, indent=2)}
Total: ${categorized.total:.2f}

GOAL: {goal_text}

RULES:
1. Never cut essentials below survival level
2. Cut discretionary spending first (entertainment, dining, shopping)
3. Propose specific dollar amounts per category
4. Explain your reasoning clearly

Respond in this exact JSON format:
{{
    "cuts": {{"category": dollar_amount}},
    "savings": total_monthly_savings,
    "explanation": "Your explanation here"
}}"""

    return prompt


def parse_recommendation(raw_response: str, original_total: float) -> BudgetPlan:
    """Parse Qwen's response into a BudgetPlan."""
    try:
        # Extract JSON from response
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        data = json.loads(raw_response[start:end])

        cuts = data.get("cuts", {})
        savings = data.get("savings", 0)
        explanation = data.get("explanation", "")

        return BudgetPlan(
            original_spending=original_total,
            proposed_spending=original_total - savings,
            savings=savings,
            cuts=cuts,
            explanation=explanation
        )
    except (json.JSONDecodeError, ValueError):
        return BudgetPlan(
            original_spending=original_total,
            proposed_spending=original_total,
            savings=0,
            cuts={},
            explanation="Failed to parse recommendation. Please try again."
        )


def get_budget_recommendation(
    categorized_transactions: CategorizedTransactions,
    savings_goal
) -> dict:
    """Call Qwen API and return structured recommendation."""
    prompt = build_prompt(categorized_transactions, savings_goal)

    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            timeout=30
        )

        if response.status_code != 200:
            return {
                "error": "Qwen API timeout or error",
                "fallback": True,
                "original_total": categorized_transactions.total,
                "essential": categorized_transactions.essential,
                "discretionary": categorized_transactions.discretionary
            }

        plan = parse_recommendation(response.output.text, categorized_transactions.total)

        return {
            "original_spending": plan.original_spending,
            "proposed_spending": plan.proposed_spending,
            "savings": plan.savings,
            "cuts": plan.cuts,
            "explanation": plan.explanation,
            "essential": categorized_transactions.essential,
            "discretionary": categorized_transactions.discretionary
        }

    except Exception as e:
        return {
            "error": f"Qwen API timeout: {str(e)}",
            "fallback": True,
            "original_total": categorized_transactions.total,
            "essential": categorized_transactions.essential,
            "discretionary": categorized_transactions.discretionary
        }