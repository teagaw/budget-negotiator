# src/negotiation.py
import os
import json
import dashscope
from dashscope import Generation
from src.qwen_client import QwenAPIError, extract_json_from_response

dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


def _build_negotiation_prompt(
    categorized: dict,
    previous_plan: dict,
    user_objection: str
) -> str:
    """Build the negotiation prompt for Qwen."""
    return f"""You are a budget negotiator in a conversation with a user.

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


def _call_qwen_negotiation(prompt: str) -> dict:
    """Call Qwen API for negotiation. Raises QwenAPIError on failure."""
    response = Generation.call(
        model="qwen-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
        timeout=30
    )

    if response.status_code != 200:
        raise QwenAPIError(f"Qwen API returned status {response.status_code}")

    return extract_json_from_response(response.output.text)


def generate_counter_offer(
    categorized: dict,
    previous_plan: dict,
    user_objection: str
) -> dict:
    """
    Generate counter-offer using Qwen API on EVERY turn.
    No local arithmetic — the LLM reasons about the tradeoff.
    """
    prompt = _build_negotiation_prompt(categorized, previous_plan, user_objection)

    try:
        parsed_response = _call_qwen_negotiation(prompt)

        original_spending = categorized.get("total", 0)
        savings = parsed_response.get("savings", 0)

        return {
            "cuts": parsed_response.get("cuts", {}),
            "savings": savings,
            "proposed_spending": original_spending - savings,
            "explanation": parsed_response.get("explanation", ""),
            "essential": categorized.get("essential", {}),
            "discretionary": categorized.get("discretionary", {}),
            "original_spending": original_spending
        }

    except (QwenAPIError, json.JSONDecodeError, KeyError) as e:
        # Propagate error to caller instead of silently swallowing
        return {
            "error": f"Negotiation failed: {str(e)}",
            "fallback": True,
            **previous_plan
        }


def validate_ambiguity(categorized: dict, plan: dict) -> bool:
    """Sanity check for ambiguous input responses.
    Returns True if plan is valid, False if nonsensical."""
    original = categorized.get("total", 0)
    savings = plan.get("savings", 0)
    proposed = plan.get("proposed_spending", 0)
    return savings < original and proposed > 0


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
