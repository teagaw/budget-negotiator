"""
Rules engine for parsing and categorizing transactions.
This module handles CSV parsing and transaction categorization.
"""
from typing import List, Dict, Any


def parse_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse raw transaction data into a standardized format.
    
    Args:
        transactions: List of raw transaction dictionaries
        
    Returns:
        List of parsed transaction dictionaries
    """
    parsed = []
    for txn in transactions:
        parsed_txn = {
            "amount": float(txn.get("amount", 0)),
            "category": txn.get("category", "uncategorized"),
            "description": txn.get("description", ""),
            "date": txn.get("date", ""),
        }
        parsed.append(parsed_txn)
    return parsed


def categorize_transactions(parsed_transactions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group transactions by category.
    
    Args:
        parsed_transactions: List of parsed transaction dictionaries
        
    Returns:
        Dictionary mapping category names to lists of transactions
    """
    categorized = {}
    for txn in parsed_transactions:
        category = txn["category"]
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(txn)
    return categorized
