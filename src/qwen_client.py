"""
Qwen API client for budget negotiation reasoning.
This module handles all Qwen Cloud API interactions.
"""
import os
import dashscope
from dashscope import Generation
from typing import Dict, Any, List


def get_budget_recommendation(
    categorized_transactions: Dict[str, List[Dict[str, Any]]],
    savings_goal: str = "auto"
) -> Dict[str, Any]:
    """
    Get budget recommendation using Qwen API.
    
    Args:
        categorized_transactions: Transactions grouped by category
        savings_goal: Target savings goal (or "auto" for automatic)
        
    Returns:
        Dictionary with budget recommendation
    """
    # Build prompt for Qwen
    prompt = f"""Analyze these categorized transactions and provide budget recommendations:
{categorized_transactions}

Savings goal: {savings_goal}

Please provide:
1. Total spending by category
2. Top 3 categories to cut
3. Specific dollar amounts to reduce
4. Estimated monthly savings"""
    
    response = Generation.call(
        model="qwen-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "recommendation": response.output.text,
        "savings_goal": savings_goal,
        "categories_analyzed": list(categorized_transactions.keys())
    }


def get_counter_offer(
    categorized: Dict[str, List[Dict[str, Any]]],
    previous_plan: Dict[str, Any],
    user_objection: str
) -> Dict[str, Any]:
    """
    Generate a counter-offer during negotiation using Qwen API.
    
    Args:
        categorized: Current categorized transactions
        previous_plan: The previous budget plan
        user_objection: User's objection to the plan
        
    Returns:
        Dictionary with counter-offer
    """
    prompt = f"""Previous budget plan: {previous_plan}
User objection: {user_objection}
Current spending: {categorized}

Generate a counter-offer that addresses the user's objection while maintaining savings goals."""
    
    response = Generation.call(
        model="qwen-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "counter_offer": response.output.text,
        "addresses_objection": user_objection
    }
