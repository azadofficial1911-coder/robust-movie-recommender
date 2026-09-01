"""Recommendation-quality metrics."""
import math

def _check(a,p):
    if len(a)!=len(p) or not a: raise ValueError("Inputs must have the same non-zero length.")

def rmse(actual,predicted):
    _check(actual,predicted); return math.sqrt(sum((a-p)**2 for a,p in zip(actual,predicted))/len(actual))

def mae(actual,predicted):
    _check(actual,predicted); return sum(abs(a-p) for a,p in zip(actual,predicted))/len(actual)

def precision_at_k(recommended,relevant,k):
    if k<=0: raise ValueError("k must be positive.")
    r=set(relevant); top=list(recommended)[:k]; return sum(x in r for x in top)/k

def recall_at_k(recommended,relevant,k):
    if k<=0: raise ValueError("k must be positive.")
    r=set(relevant)
    if not r: return 0.0
    return sum(x in r for x in list(recommended)[:k])/len(r)
