"""Validation-only random search for fusion weights. Test split remains untouched."""
import random,json
from .synthetic_data import generate_dataset
from .convergence_engine import compute_actor_linkage,DEFAULT_WEIGHTS
DECISION_THRESHOLD=50.0
SIGNALS=list(DEFAULT_WEIGHTS)

def _score_weights(weights,identities,pairs,threshold=DECISION_THRESHOLD):
    tp=fp=fn=tn=0
    for p in pairs:
        pred=compute_actor_linkage(identities[p.id_a],identities[p.id_b],weights).score>=threshold
        if pred and p.ground_truth_linked:tp+=1
        elif pred and not p.ground_truth_linked:fp+=1
        elif not pred and p.ground_truth_linked:fn+=1
        else:tn+=1
    precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0; f1=2*precision*recall/(precision+recall) if precision+recall else 0; fpr=fp/(fp+tn) if fp+tn else 0
    return {"precision":precision,"recall":recall,"f1":f1,"fpr":fpr,"tp":tp,"fp":fp,"fn":fn,"tn":tn}

def random_search(n_trials=300,seed=7):
    rng=random.Random(seed); ds=generate_dataset(20,42); best=None
    for _ in range(n_trials):
        raw=[rng.uniform(.5,2.0) for _ in SIGNALS]; total=sum(raw); weights={s:100*raw[i]/total for i,s in enumerate(SIGNALS)}
        m=_score_weights(weights,ds["identities"],ds["pairs"]["val"])
        if best is None or (m["f1"],-m["fpr"])>(best["metrics"]["f1"],-best["metrics"]["fpr"]): best={"weights":weights,"metrics":m}
    return best

if __name__=="__main__":
    best=random_search(); print(json.dumps(best,indent=2));
    with open("tuned_weights.json","w") as f: json.dump(best["weights"],f,indent=2)
