"""Held-out synthetic evaluation for the frozen fusion weights."""
import json,os
from .synthetic_data import generate_dataset
from .convergence_engine import compute_actor_linkage,DEFAULT_WEIGHTS
from .tune_weights import _score_weights,DECISION_THRESHOLD

def load_tuned_weights():
    for p in [os.path.join(os.path.dirname(__file__),"..","tuned_weights.json"),os.path.join(os.path.dirname(__file__),"tuned_weights.json"),"tuned_weights.json"]:
        if os.path.exists(p):
            with open(p) as f:return json.load(f)
    return DEFAULT_WEIGHTS

def evaluate_on_test_set(weights=None,seed=42,n_scenarios_per_type=20):
    weights=weights or load_tuned_weights(); ds=generate_dataset(n_scenarios_per_type,seed); ids=ds["identities"]; pairs=ds["pairs"]["test"]
    metrics=_score_weights(weights,ids,pairs)
    by={}
    for p in pairs:
        r=compute_actor_linkage(ids[p.id_a],ids[p.id_b],weights); pred=r.score>=DECISION_THRESHOLD; e=by.setdefault(p.scenario_type,{"correct":0,"total":0}); e["total"]+=1; e["correct"]+=int(pred==p.ground_truth_linked)
    return {"weights_used":weights,"overall_metrics":metrics,"dataset_split":{"train":int(len(ds["pairs"]["train"])),"validation":int(len(ds["pairs"]["val"])),"held_out_test":int(len(ds["pairs"]["test"]))},"by_scenario_type":by,"n_test_pairs":len(pairs),"decision_threshold":DECISION_THRESHOLD,"caveat":"Controlled synthetic evaluation only. These metrics validate prototype methodology under synthetic ground truth and do not establish real-world de-anonymization performance."}
