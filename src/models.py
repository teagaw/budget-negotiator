# src/models.py
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Transaction:
    amount: float
    category: str
    description: str


@dataclass
class CategorizedTransactions:
    essential: Dict[str, float] = field(default_factory=dict)
    discretionary: Dict[str, float] = field(default_factory=dict)
    total: float = 0.0


@dataclass
class BudgetPlan:
    original_spending: float
    proposed_spending: float
    savings: float
    cuts: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""