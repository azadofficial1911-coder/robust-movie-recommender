"""Recommendation-quality metrics."""
from __future__ import annotations
import math
from typing import Iterable, Sequence

def rmse(actual: Sequence[float], predicted: Sequence[float]) -> float:
    if len(actual) != len(predicted) or not actual: raise ValueError("actual and predicted must have the same non-zero length.")
    return math.sqrt(sum((a-p)**2 for a,p in zip(actual,predicted))/len(actual))

def mae(actual: Sequence[float], predicted: Sequence[float]) -> float:
    if len(actual) != len(predicted) or not actual: raise ValueError("actual and predicted must have the same non-zero length.")
    return sum(abs(a-p) for a,p in zip(actual,predicted))/len(actual)

def precision_at_k(recommended: Iterable, relevant: Iterable, k: int) -> float:
    if k <= 0: raise ValueError("k must be positive.")
    return sum(x in set(relevant) for x in list(recommended)[:k])/k

def recall_at_k(recommended: Iterable, relevant: Iterable, k: int) -> float:
    if k <= 0: raise ValueError("k must be positive.")
    rel = set(relevant)
    if not rel: return 0.0
    return sum(x in rel for x in list(recommended)[:k])/len(rel)
