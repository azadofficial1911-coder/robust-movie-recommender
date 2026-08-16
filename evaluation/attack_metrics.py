"""Attack-impact evaluation metrics."""
from __future__ import annotations
from typing import Sequence

def target_rank(items: Sequence, target_movie):
    try: return list(items).index(target_movie)+1
    except ValueError: return None

def hit_rate(hit_values: Sequence[bool]) -> float:
    if not hit_values: raise ValueError("hit_values must not be empty.")
    return sum(bool(x) for x in hit_values)/len(hit_values)
