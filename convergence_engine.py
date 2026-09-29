"""Explainable evidence fusion engine."""
from dataclasses import dataclass
from typing import Dict,Tuple
from .synthetic_data import Identity
from . import similarity as sim

DEFAULT_WEIGHTS={"temporal":22,"account":16,"infrastructure":20,"activity":16,"interaction_network":16,"linguistic":10}
CONTRADICTION_MULTIPLIER=1.5
CONTRADICTION_THRESHOLD=.20
SUPPORTING_THRESHOLD=.50
SUPPORTING_HIGH_THRESHOLD=.60

@dataclass
class ConvergenceResult:
    score:float; confidence_band:str; contributions:Dict[str,float]; contribution_pct:Dict[str,float]
    supporting_evidence:Dict[str,dict]; contradictory_evidence:Dict[str,dict]; insufficient_evidence:Dict[str,dict]; reasoning:list
    privacy_context:dict

def _band(score):
    if score<30:return "LOW"
    if score<50:return "INCONCLUSIVE"
    if score<70:return "MODERATE"
    return "STRONG"

def compute_actor_linkage(a,b,weights=None):
    weights=weights or DEFAULT_WEIGHTS
    signals={"temporal":sim.temporal_similarity(a,b),"account":sim.account_similarity(a,b),"infrastructure":sim.infrastructure_similarity(a,b),"activity":sim.activity_similarity(a,b),"interaction_network":sim.interaction_network_similarity(a,b),"linguistic":sim.linguistic_similarity(a,b)}
    contributions={}; supporting={}; contradicting={}; insufficient={}; reasoning=[]
    prevailing=sum(signals[s][0] for s in ("temporal","account","activity","interaction_network"))/4
    for name,(value,detail) in signals.items():
        weight=weights.get(name,0)
        contradictory=prevailing>=SUPPORTING_HIGH_THRESHOLD and value<=CONTRADICTION_THRESHOLD
        if contradictory:
            penalty=-weight*CONTRADICTION_MULTIPLIER*(1-value)
            contributions[name]=round(penalty,2); contradicting[name]=detail
            reasoning.append(f"Contradictory evidence: {name} similarity was {value:.2f}; a {CONTRADICTION_MULTIPLIER}× contradiction penalty was applied to its own weight.")
        else:
            points=weight*value; contributions[name]=round(points,2)
            if value>=SUPPORTING_THRESHOLD:
                supporting[name]=detail; reasoning.append(f"Supporting evidence: {name} similarity {value:.2f} contributed {points:.1f} points.")
            else:
                insufficient[name]=detail; reasoning.append(f"Insufficient evidence: {name} similarity {value:.2f} did not meet the supporting threshold.")
    raw=sum(contributions.values()); score=max(0,min(100,raw)); total_abs=sum(abs(x) for x in contributions.values()) or 1
    pct={k:round(abs(v)/total_abs*100,1) for k,v in contributions.items()}
    reasoning.append("Privacy/anonymity indicators (Tor, VPN, cryptocurrency, encrypted messaging) were excluded from the attribution score.")
    reasoning.append("Score is strength-of-evidence, not probability of guilt or identity certainty.")
    return ConvergenceResult(round(score,1),_band(score),contributions,pct,supporting,contradicting,insufficient,reasoning,sim.privacy_context(a,b))
