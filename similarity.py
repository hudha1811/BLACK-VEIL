"""Explainable similarity functions used by Convergence."""
import math
from collections import Counter
from typing import Tuple, Dict
from .synthetic_data import Identity

ACCOUNT_DECAY_DAYS = 60
POSTING_DECAY_MINUTES = 120


def _cosine(v1,v2):
    dot=sum(a*b for a,b in zip(v1,v2)); n1=math.sqrt(sum(a*a for a in v1)); n2=math.sqrt(sum(b*b for b in v2))
    return 0.0 if n1==0 or n2==0 else max(0.0,min(1.0,dot/(n1*n2)))


def temporal_similarity(a:Identity,b:Identity)->Tuple[float,Dict]:
    ha=[0]*24; hb=[0]*24
    for h in a.active_hours: ha[h]+=1
    for h in b.active_hours: hb[h]+=1
    sim=_cosine(ha,hb)
    matching=[i for i in range(24) if ha[i]>0 and hb[i]>0]
    # Convert adjacent matching hours into compact windows.
    windows=[]
    if matching:
        start=prev=matching[0]
        for h in matching[1:]:
            if h==prev+1: prev=h
            else: windows.append((start,prev)); start=prev=h
        windows.append((start,prev))
    return sim,{"matching_activity_hours":matching,"matching_activity_windows":[f"{s:02d}:00–{e+1:02d}:00" for s,e in windows],"observation_period_days":14,"similarity":round(sim,3)}


def account_similarity(a,b):
    days=abs((a.account_creation_ts-b.account_creation_ts).total_seconds())/86400
    creation=max(0.0,1-days/ACCOUNT_DECAY_DAYS)
    diff=abs(a.posting_interval_minutes-b.posting_interval_minutes)
    posting=max(0.0,1-diff/POSTING_DECAY_MINUTES)
    sim=.4*creation+.6*posting
    return sim,{"creation_gap_days":round(days,2),"posting_interval_diff_minutes":round(diff,2),"creation_decay_days":ACCOUNT_DECAY_DAYS,"posting_decay_minutes":POSTING_DECAY_MINUTES,"similarity":round(sim,3)}


def infrastructure_similarity(a,b):
    keys=["tls","service","certificate","server","asn"]
    fa=getattr(a,"infra_features",{}) or {}; fb=getattr(b,"infra_features",{}) or {}
    matches=[k for k in keys if fa.get(k) and fa.get(k)==fb.get(k)]
    if not fa or not fb:
        sim=.95 if a.infra_fingerprint==b.infra_fingerprint else .05
        mode="exact" if sim>.9 else "none"
    else:
        overlap=len(matches)/len(keys)
        if overlap==1: sim=.95; mode="exact"
        elif overlap>0: sim=.5+.3*overlap; mode="partial"
        else: sim=.05; mode="none"
    explicit = {
        "ssl_certificates": _shared(a,b,"ssl_certificates"),
        "certificate_domain_links": [x for x in (getattr(a,"certificate_domain_links",[]) or []) if x in (getattr(b,"certificate_domain_links",[]) or [])],
        "clearnet_domains": _shared(a,b,"clearnet_domains"),
        "service_banners": _shared(a,b,"service_banners"),
        "exposed_server_status": _shared(a,b,"exposed_server_status"),
        "descriptor_inconsistencies": _shared(a,b,"descriptor_inconsistencies"),
    }
    observations=[]
    if explicit["ssl_certificates"]: observations.append("Shared SSL certificate identifier(s).")
    if explicit["certificate_domain_links"]: observations.append("SSL certificate tied to the same clearnet-domain relationship.")
    if explicit["clearnet_domains"]: observations.append("Shared clearnet domain identifier(s).")
    if explicit["service_banners"]: observations.append("Shared service/default banner(s).")
    if explicit["exposed_server_status"]: observations.append("Shared exposed server-status observation(s).")
    if explicit["descriptor_inconsistencies"]: observations.append("Shared descriptor inconsistency marker(s).")
    return sim,{"identity_a_infra":a.infra_fingerprint,"identity_b_infra":b.infra_fingerprint,"matched_components":matches,"match_ratio":round(len(matches)/len(keys),2),"match_type":mode,"identity_a_components":fa,"identity_b_components":fb,"similarity":round(sim,3),"ps26151_infrastructure_evidence":explicit,"observations":observations,"note":"Infrastructure score uses TLS/service/certificate/server/ASN component overlap; PS-specific clearnet/certificate/server-status/descriptor objects are explicitly represented as corroborating evidence."}


def activity_similarity(a,b):
    ca,cb=Counter(a.activity_sequence),Counter(b.activity_sequence); keys=sorted(set(ca)|set(cb)); v1=[ca.get(k,0) for k in keys]; v2=[cb.get(k,0) for k in keys]; sim=_cosine(v1,v2)
    strongest=sorted(keys,key=lambda k:min(ca.get(k,0),cb.get(k,0)),reverse=True)[:3]
    return sim,{"identity_a_actions":dict(ca),"identity_b_actions":dict(cb),"strongest_matching_behaviors":strongest,"similarity":round(sim,3)}


def interaction_network_similarity(a,b):
    va=getattr(a,"interaction_vector",[0]*5); vb=getattr(b,"interaction_vector",[0]*5); sim=_cosine(va,vb)
    ca=set(getattr(a,"interaction_counterparties",[]) or []); cb=set(getattr(b,"interaction_counterparties",[]) or []); shared=sorted(ca&cb)
    return sim,{"identity_a_interaction_vector":va,"identity_b_interaction_vector":vb,"shared_counterparties":shared,"shared_counterparty_count":len(shared),"similarity":round(sim,3),"note":"Behavioral interaction patterns are attribution evidence; privacy/anonymity tools are excluded from this signal."}

# Backward-compatible alias; it now means interaction behavior, not privacy tools.
network_similarity=interaction_network_similarity


def privacy_context(a,b):
    return {"identity_a":{"tor":a.uses_tor,"vpn":a.uses_vpn,"cryptocurrency":a.uses_crypto,"encrypted_messaging":a.uses_encrypted_msg},"identity_b":{"tor":b.uses_tor,"vpn":b.uses_vpn,"cryptocurrency":b.uses_crypto,"encrypted_messaging":b.uses_encrypted_msg},"contributes_to_score":False,"note":"Contextual indicators only — never increase or decrease attribution confidence."}


def linguistic_similarity(a,b):
    sim=_cosine(a.writing_style_vector,b.writing_style_vector)
    return sim,{"similarity":round(sim,3),"features":["sentence length","punctuation pattern","function-word usage","vocabulary patterns","n-gram distribution"],"representation":"Synthetic stylometric representation","note":"Prototype stylometry is synthetic; the similarity computation itself is cosine similarity."}


def _shared(a, b, field):
    return sorted(set(getattr(a, field, []) or []) & set(getattr(b, field, []) or []))


def threat_actor_intelligence(a, b):
    """Explicit PS 26151 intelligence objects. This layer is explainable corroboration/context and is NOT a seventh score signal."""
    fields = ["handles", "pgp_keys", "wallets", "trust_links", "marketplaces", "clearnet_domains", "ssl_certificates", "service_banners", "exposed_server_status", "descriptor_inconsistencies", "tor_services", "persona_history"]
    matches = {f: _shared(a, b, f) for f in fields}
    cert_links_a = getattr(a, "certificate_domain_links", []) or []
    cert_links_b = getattr(b, "certificate_domain_links", []) or []
    shared_links = [x for x in cert_links_a if x in cert_links_b]
    # Rebranded/migrated persona evidence is explicitly surfaced, never inferred from privacy tooling.
    persona_a = set(getattr(a, "persona_history", []) or [])
    persona_b = set(getattr(b, "persona_history", []) or [])
    rebrand_overlap = sorted(persona_a & persona_b)
    total_matches = sum(len(v) for v in matches.values()) + len(shared_links)
    observations = []
    if matches["handles"]: observations.append("Shared handle(s): " + ", ".join(matches["handles"]))
    if matches["pgp_keys"]: observations.append("Shared PGP key(s): " + ", ".join(matches["pgp_keys"]))
    if matches["wallets"]: observations.append("Shared wallet identifier(s): " + ", ".join(matches["wallets"]))
    if matches["trust_links"]: observations.append("Shared trust link(s): " + ", ".join(matches["trust_links"]))
    if matches["marketplaces"]: observations.append("Shared marketplace presence: " + ", ".join(matches["marketplaces"]))
    if matches["clearnet_domains"]: observations.append("Shared clearnet domain(s): " + ", ".join(matches["clearnet_domains"]))
    if shared_links: observations.append("Shared SSL-certificate ↔ clearnet-domain relationship(s) detected.")
    if matches["service_banners"]: observations.append("Shared service/default banner(s): " + ", ".join(matches["service_banners"]))
    if matches["exposed_server_status"]: observations.append("Shared exposed server-status observation(s).")
    if matches["descriptor_inconsistencies"]: observations.append("Shared descriptor inconsistency marker(s).")
    if matches["tor_services"]: observations.append("Shared hidden-service identifier(s).")
    if rebrand_overlap: observations.append("Overlapping persona-history marker(s): " + ", ".join(rebrand_overlap))
    return {
        "objects": {
            "identity_a": {f: getattr(a, f, []) for f in fields},
            "identity_b": {f: getattr(b, f, []) for f in fields},
            "certificate_domain_links_a": cert_links_a,
            "certificate_domain_links_b": cert_links_b,
        },
        "matches": matches,
        "shared_certificate_domain_links": shared_links,
        "persona_history_overlap": rebrand_overlap,
        "persona_analysis": {
            "activity_similarity": round(activity_similarity(a,b)[0],3),
            "stylometric_similarity": round(linguistic_similarity(a,b)[0],3),
            "persona_history_overlap": rebrand_overlap,
            "interpretation": "Explainable persona analysis combines behavioral profiling and stylometric evidence; it is not a separate seventh score signal."
        },
        "match_count": total_matches,
        "observations": observations,
        "contributes_to_six_signal_score": False,
        "note": "Threat-Actor Intelligence Layer explicitly maps PS 26151 entities. These corroborating objects are not treated as a separate seventh score signal."
    }
