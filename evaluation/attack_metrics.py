"""Attack-impact metrics."""
def target_rank(recommendations,target_movie):
    try: return list(recommendations).index(target_movie)+1
    except ValueError: return None

def target_score(predicted_scores,target_movie):
    return predicted_scores.get(target_movie)

def hit_rate(hit_values):
    if not hit_values: raise ValueError("hit_values must not be empty.")
    return sum(bool(x) for x in hit_values)/len(hit_values)
