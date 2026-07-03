# src/negotiation.py
import os
import json
import dashscope
from dashscope import Generation

dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


def generate_counter_offer(
    categorized: dict,
    previous_plan: dict,
    user_objection: str
) -> dict:
    """
    Generate counter-offer using Qwen API on EVERY turn.
    No local arithmetic — the LLM reasons about the tradeoff.
    """
    prompt = f"""You are a budget negotiator in a conversation with a user.

ORIGINAL SPENDING DATA:
Essential: {json.dumps(categorized.get("essential", {}), indent=2)}
Discretionary: {json.dumps(categorized.get("discretionary", {}), indent=2)}
Total: ${categorized.get("total", 0):.2f}

PREVIOUS PLAN YOU PROPOSED:
{json.dumps(previous_plan, indent=2)}

USER'S OBJECTION:
"{user_objection}"

TASK:
The user rejected part of your previous plan. Read their objection carefully.
They may reject a specific category, explain why, or propose an alternative.

Adjust the plan based on their feedback:
- If they reject a cut, reduce it or find savings elsewhere
- If they propose an alternative, incorporate it
- Always maintain the total savings target if possible
- Never cut essentials

Respond in this exact JSON format:
{{
    "cuts": {{"category": dollar_amount}},
    "savings": total_monthly_savings,
    "explanation": "Your explanation acknowledging their feedback and your adjustment"
}}"""

    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            timeout=30
        )

        if response.status_code != 200:
            # Fallback: return previous plan unchanged
            return previous_plan

        # Parse Qwen's response
        raw = response.output.text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])

        return {
            "cuts": data.get("cuts", {}),
            "savings": data.get("savings", 0),
            "explanation": data.get("explanation", ""),
            "essential": categorized.get("essential", {}),
            "discretionary": categorized.get("discretionary", {}),
            "original_spending": categorized.get("total", 0)
        }

    except Exception:
        # On any error, return previous plan unchanged
        return previous_plan


def format_budget_breakdown(plan: dict) -> str:
    """Format budget plan as readable text."""
    lines = [
        "=== BUDGET NEGOTIATION PLAN ===",
        f"\nOriginal Spending: ${plan.get('original_spending', 0):,.2f}",
        f"Proposed Spending: ${plan.get('proposed_spending', 0):,.2f}",
        f"Monthly Savings:   ${plan.get('savings', 0):,.2f}",
        "\n--- PROPOSED CUTS ---"
    ]

    for category, amount in plan.get("cuts", {}).items():
        lines.append(f"  {category}: -${amount:.2f}")

    lines.append(f"\n--- REASONING ---")
    lines.append(plan.get("explanation", ""))

    return "\n".join(lines)