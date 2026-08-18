"""Detection evaluation metrics."""
from __future__ import annotations

def confusion_counts(true_labels, predicted_labels, positive_label="suspicious") -> dict:
    if len(true_labels) != len(predicted_labels): raise ValueError("Label lists must have the same length.")
    tp=fp=tn=fn=0
    for actual,predicted in zip(true_labels,predicted_labels):
        ap=actual==positive_label; pp=predicted==positive_label
        if ap and pp: tp+=1
        elif not ap and pp: fp+=1
        elif not ap and not pp: tn+=1
        else: fn+=1
    return {"tp":tp,"fp":fp,"tn":tn,"fn":fn}

def detection_metrics(true_labels, predicted_labels, positive_label="suspicious") -> dict:
    c=confusion_counts(true_labels,predicted_labels,positive_label)
    tp,fp,tn,fn=(c[k] for k in ("tp","fp","tn","fn"))
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    fpr=fp/(fp+tn) if fp+tn else 0.0
    return {**c,"precision":precision,"recall":recall,"f1":f1,"false_positive_rate":fpr}
