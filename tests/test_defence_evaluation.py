"""Basic tests for Achintha's modules."""
import pandas as pd
from defence.remove_profiles import get_suspicious_user_ids, remove_suspicious_profiles
from evaluation.recommender_metrics import rmse, mae, precision_at_k, recall_at_k
from evaluation.detection_metrics import confusion_counts, detection_metrics
from evaluation.attack_metrics import target_rank, target_score, hit_rate

def test_defence():
    d=pd.DataFrame({"user_id":[1,2,3],"predicted_label":["genuine","suspicious","suspicious"]})
    assert get_suspicious_user_ids(d)=={2,3}
    r=pd.DataFrame({"user_id":[1,1,2,3],"movie_id":[10,11,12,13],"rating":[4,5,2,3]})
    assert remove_suspicious_profiles(r,{2})["user_id"].tolist()==[1,1,3]

def test_recommender_metrics():
    assert mae([1,2],[1,3])==0.5
    assert rmse([1,2],[1,3])>0
    assert precision_at_k([1,2,3],[2,4],3)==1/3
    assert recall_at_k([1,2,3],[2,4],3)==0.5

def test_detection():
    t=["suspicious","genuine","genuine","suspicious"]; p=["suspicious","suspicious","genuine","genuine"]
    assert confusion_counts(t,p)=={"tp":1,"fp":1,"tn":1,"fn":1}
    m=detection_metrics(t,p); assert m["precision"]==m["recall"]==m["f1"]==m["false_positive_rate"]==0.5

def test_attack():
    assert target_rank([10,20,30],20)==2
    assert target_rank([10,20,30],99) is None
    assert target_score({20:4.2},20)==4.2
    assert hit_rate([True,False,True])==2/3
