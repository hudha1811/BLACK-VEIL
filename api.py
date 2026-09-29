"""Convergence Explainable Actor-Linkage & Attribution Platform API."""
import copy,csv,io,hashlib,random,json
from datetime import datetime,timedelta
from dataclasses import asdict
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,Response
from core.synthetic_data import generate_dataset,Identity,_make_identity
from core.convergence_engine import compute_actor_linkage,DEFAULT_WEIGHTS,CONTRADICTION_MULTIPLIER
from core.graph_builder import build_case_graph
from core.integrity import build_integrity_chain,hash_identity_evidence
from core.report_generator import generate_report,generate_pdf_report
from core.evaluate import evaluate_on_test_set,load_tuned_weights
from core import similarity as sim

app=FastAPI(title="Convergence — Explainable Actor-Linkage & Attribution Platform")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

_DATASET=generate_dataset(15,42); _IDENTITIES=_DATASET["identities"]; _WEIGHTS=load_tuned_weights(); _AUDIT=[]
_rng=random.Random(99)

SIGNAL_LABELS={"temporal":"Temporal","account":"Account","infrastructure":"Infrastructure","activity":"Activity","interaction_network":"Interaction Network","linguistic":"Linguistic / Stylometry"}
SIGNAL_FUNCS={"temporal":sim.temporal_similarity,"account":sim.account_similarity,"infrastructure":sim.infrastructure_similarity,"activity":sim.activity_similarity,"interaction_network":sim.interaction_network_similarity,"linguistic":sim.linguistic_similarity}

def audit(event,details=None):
    row={"timestamp":datetime.utcnow().isoformat()+"Z","event":event,"details":details or {}}
    _AUDIT.append(row); return row

def _parts(rng,tag,conflict=False):
    return {"tls":f"tls_{tag}","service":f"svc_{tag}","certificate":f"cert_{tag}","server":f"srv_{tag}","asn":f"asn_{tag}"}

def _build_demo_case_a():
    a=_make_identity("caseA_researcher","caseA_actor","legitimate_privacy_user",[9,10,11,20,21],"infra_A_PRIVACY",[_rng.uniform(0,1) for _ in range(6)],_rng,1.5,.12,True)
    b=_make_identity("caseA_unrelated","caseA_other","independent_unrelated_users",[2,3,4],"infra_B_UNRELATED",[_rng.uniform(0,1) for _ in range(6)],_rng,1.5,.12,False)
    b.account_creation_ts = a.account_creation_ts + timedelta(days=75)
    b.posting_interval_minutes = a.posting_interval_minutes + 220
    b.activity_sequence = ["withdraw","upload","search","withdraw","upload","search","withdraw"]
    b.interaction_vector = [1,2,1,8,9]
    b.interaction_counterparties = ["cp_unrelated_1","cp_unrelated_2"]
    a.writing_style_vector = [1,0,0,0,0,0]
    b.writing_style_vector = [0,1,0,0,0,0]
    a.interaction_vector = [10,0,0,0,0]
    b.interaction_vector = [0,10,0,0,0]
    b.infra_features = {"tls":"tls_UNIQUE_B","service":"svc_UNIQUE_B","certificate":"cert_UNIQUE_B","server":"srv_UNIQUE_B","asn":"asn_UNIQUE_B"}
    return a,b

def _build_demo_case_b():
    style=[_rng.uniform(0,1) for _ in range(6)]; iv=[_rng.uniform(8,18) for _ in range(5)]; parts=_parts(_rng,"DARK")
    a=_make_identity("caseB_alpha","caseB_actor","same_actor_multi_identity",[9,10,11,20,21],"infra_DARKNET_CLUSTER_7",style,_rng,.5,.02,False,iv,parts)
    b=_make_identity("caseB_beta","caseB_actor","same_actor_multi_identity",[9,10,11,20,21],"infra_DARKNET_CLUSTER_7",style,_rng,.5,.02,False,iv,parts)
    b.account_creation_ts=a.account_creation_ts; b.posting_interval_minutes=a.posting_interval_minutes; b.activity_sequence=list(a.activity_sequence); b.interaction_counterparties=list(a.interaction_counterparties)
    return a,b

def _build_demo_case_c():
    style_a=[.8,.6,.4,.7,.5,.6]; style_b=[.2,.8,.6,.4,.7,.3]
    a=_make_identity("caseC_original","caseC_actor_A","ambiguous_case",[9,10,11,20,21],"infra_C_A",style_a,_rng,.8,.05,False,[10,8,7,4,5],_parts(_rng,"C1"))
    b=_make_identity("caseC_candidate","caseC_actor_B","ambiguous_case",[9,10,11,20,21],"infra_C_B",style_b,_rng,1.0,.1,False,[4,9,3,8,2],_parts(_rng,"C2"))
    # Intentionally mixed signals for INCONCLUSIVE.
    b.account_creation_ts=a.account_creation_ts+timedelta(days=21); b.posting_interval_minutes=a.posting_interval_minutes+55
    b.activity_sequence=list(a.activity_sequence[:18])+["upload","withdraw","search"]
    return a,b

_CASE_A=_build_demo_case_a(); _CASE_B=_build_demo_case_b(); _CASE_C=_build_demo_case_c()

# Explicit PS 26151 demonstration objects: the strong case converges through
# handles, PGP, wallets, trust, marketplace, certificate/domain, and persona history.
_ba,_bb=_CASE_B
_shared_intel={
    "handles":["ShadowFox"],
    "pgp_keys":["PGP_SHADOWFOX_7821"],
    "wallets":["WALLET_SHADOWFOX_91"],
    "trust_links":["TRUST_MARKET_7"],
    "marketplaces":["market_alpha"],
    "clearnet_domains":["shadowfox.example"],
    "ssl_certificates":["cert_DARK"],
    "certificate_domain_links":[{"certificate":"cert_DARK","domain":"shadowfox.example"}],
    "service_banners":["svc_DARK"],
    "exposed_server_status":["server-status: enabled"],
    "descriptor_inconsistencies":["descriptor_version_overlap"],
    "tor_services":["shadowfox_onion_91"],
    "persona_history":["ShadowFox:v1","ShadowFox:v2-rebrand"]
}
for _i in (_ba,_bb):
    for _k,_v in _shared_intel.items(): setattr(_i,_k,list(_v) if isinstance(_v,list) else _v)

# Case C intentionally shares only a small subset of identity intelligence.
_CASE_C[0].marketplaces=["market_beta"]; _CASE_C[1].marketplaces=["market_beta"]
for ident in (*_CASE_A,*_CASE_B,*_CASE_C): _IDENTITIES[ident.identity_id]=ident

def _identity_summary(i):
    d=asdict(i); d["account_creation_ts"]=str(d["account_creation_ts"]); return d

def _provenance(a,b,signal,value,detail,status):
    evidence_id=f"E-{a.identity_id}-{b.identity_id}-{signal}"
    observed_at=datetime.utcnow().isoformat()+"Z"
    source="synthetic_forum_dataset" if a.scenario_type!="live_investigation" else "investigator_supplied_evidence"
    payload=json.dumps({"evidence_id":evidence_id,"signal":signal,"value":value,"detail":detail,"observed_at":observed_at},sort_keys=True,default=str).encode()
    return {"evidence_id":evidence_id,"source":source,"observed_at":observed_at,"signal":signal,"value":round(value,3),"reliability":"prototype-controlled" if source.startswith("synthetic") else "investigator-declared","hash":"sha256:"+hashlib.sha256(payload).hexdigest(),"status":status,"detail":detail}

def _signal_details(a,b,result):
    rows=[]
    for signal,fn in SIGNAL_FUNCS.items():
        value,detail=fn(a,b)
        status="CONTRADICTING" if signal in result.contradictory_evidence else "SUPPORTING" if signal in result.supporting_evidence else "INSUFFICIENT"
        rows.append({"signal":signal,"label":SIGNAL_LABELS[signal],"similarity":round(value,3),"weight":_WEIGHTS.get(signal,0),"contribution":result.contributions.get(signal,0),"status":status,"evidence":detail,"provenance":_provenance(a,b,signal,value,detail,status)})
    return rows

def _timeline(a,b,result):
    # Evidence-arrival trace: each signal is incorporated sequentially, so the running score can rise or fall.
    order=["account","temporal","activity","infrastructure","interaction_network","linguistic"]
    start=min(a.account_creation_ts,b.account_creation_ts); running=0.0; rows=[]
    for idx,signal in enumerate(order):
        fn=SIGNAL_FUNCS[signal]; value,detail=fn(a,b); contribution=result.contributions[signal]; running+=contribution
        status="CONTRADICTING" if signal in result.contradictory_evidence else "SUPPORTING" if signal in result.supporting_evidence else "INSUFFICIENT"
        rows.append({"timestamp":(start+timedelta(days=idx*2)).isoformat(),"evidence_id":f"E-{a.identity_id}-{b.identity_id}-{signal}","category":SIGNAL_LABELS[signal],"description":f"{SIGNAL_LABELS[signal]} evidence incorporated into the fusion engine.","status":status,"similarity":round(value,3),"contribution":round(contribution,2),"score_after_event":round(max(0,min(100,running)),1),"detail":detail})
    return rows

def _serialize_result(a,b,result):
    return {"identity_a":a.identity_id,"identity_b":b.identity_id,"score":result.score,"confidence_band":result.confidence_band,"contributions":result.contributions,"contribution_pct":result.contribution_pct,"supporting_evidence":result.supporting_evidence,"contradictory_evidence":result.contradictory_evidence,"insufficient_evidence":result.insufficient_evidence,"signal_details":_signal_details(a,b,result),"privacy_context":result.privacy_context,"threat_actor_intelligence":sim.threat_actor_intelligence(a,b),"reasoning":result.reasoning,"methodology":{"fusion":"sum(similarity × weight), with contradiction penalty applied separately","contradiction_multiplier":CONTRADICTION_MULTIPLIER,"confidence_bands":"0–29 LOW; 30–49 INCONCLUSIVE; 50–69 MODERATE; 70–100 STRONG","score_note":"Strength of evidence, not probability of guilt or identity certainty.","threat_actor_intelligence_layer":"Explicit PS 26151 entities are represented and graphed as corroborating evidence/context, not as a seventh attribution signal."}}

def _case(case):
    return {"case-a":_CASE_A,"case-b":_CASE_B,"case-c":_CASE_C}.get(case)

def _live_identity(p,identity_id):
    def nums(v,default):
        if isinstance(v,list): return [float(x) for x in v]
        if v is None or str(v).strip()=="": return default
        return [float(x.strip()) for x in str(v).split(",") if x.strip()]
    hours=[int(x)%24 for x in nums(p.get("active_hours"),[12])]
    style=(nums(p.get("writing_style_vector"),[.5]*6)+[.5]*6)[:6]
    activity=p.get("activity_sequence",[]); activity=[str(x).strip() for x in (activity if isinstance(activity,list) else str(activity).split(",")) if str(x).strip()]
    iv=(nums(p.get("interaction_vector"),[5,5,5,5,5])+[5]*5)[:5]
    counterparties=p.get("interaction_counterparties",[]); counterparties=[str(x).strip() for x in (counterparties if isinstance(counterparties,list) else str(counterparties).split(",")) if str(x).strip()]
    try: created=datetime.fromisoformat(str(p.get("account_creation_ts")))
    except: created=datetime(2026,6,1,12,0)
    infra=str(p.get("infra_fingerprint") or "unknown")
    infra_features={k:str(p.get("infra_"+k) or f"{k}_unknown") for k in ["tls","service","certificate","server","asn"]}
    def str_list(v):
        if isinstance(v,list): return [str(x).strip() for x in v if str(x).strip()]
        return [x.strip() for x in str(v or "").split(",") if x.strip()]
    def link_list(v):
        if isinstance(v,list): return v
        return []
    cert_domain_links=link_list(p.get("certificate_domain_links"))
    return Identity(
        identity_id, f"live_{identity_id}", hours,float(p.get("session_gap_minutes") or 45),infra,created,float(p.get("posting_interval_minutes") or 120),activity or ["post","browse","login"],
        bool(p.get("uses_tor")),bool(p.get("uses_vpn")),bool(p.get("uses_crypto")),bool(p.get("uses_encrypted_msg")),style,"live_investigation",iv,counterparties,infra_features,
        str_list(p.get("handles")),str_list(p.get("pgp_keys")),str_list(p.get("wallets")),str_list(p.get("trust_links")),str_list(p.get("marketplaces")),
        str_list(p.get("clearnet_domains")),str_list(p.get("ssl_certificates")),cert_domain_links,str_list(p.get("service_banners")),str_list(p.get("exposed_server_status")),
        str_list(p.get("descriptor_inconsistencies")),str_list(p.get("tor_services")),str_list(p.get("persona_history"))
    )

def _ranked_live(payload):
    original=_live_identity(payload["original"],"live_original"); results=[]
    for idx,p in enumerate(payload["candidates"],1):
        name=str(p.get("name") or f"Candidate {idx}").strip(); cand=_live_identity(p,name.replace(" ","_")); r=compute_actor_linkage(original,cand,_WEIGHTS)
        results.append({"rank":0,"name":name,"identity":_identity_summary(cand),"result":_serialize_result(original,cand,r),"timeline":_timeline(original,cand,r),"intelligence_graph":build_case_graph({original.identity_id:original,cand.identity_id:cand},[original.identity_id,cand.identity_id],_WEIGHTS)})
    results.sort(key=lambda x:x["result"]["score"],reverse=True)
    for i,x in enumerate(results,1): x["rank"]=i
    return original,results

@app.get("/api/demo/{case}")
def get_demo(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    audit("Evidence imported",{"case":case}); r=compute_actor_linkage(*pair,_WEIGHTS); audit("Evidence fusion completed",{"case":case,"score":r.score})
    return {"label":{"case-a":"Case A — Privacy-Conscious Researcher","case-b":"Case B — Simulated Convergence","case-c":"Case C — Mixed / Inconclusive Evidence"}[case],"identities":[_identity_summary(x) for x in pair],"result":_serialize_result(*pair,r),"timeline":_timeline(*pair,r)}

@app.get("/api/demo/case-a")
def case_a(): return get_demo("case-a")
@app.get("/api/demo/case-b")
def case_b(): return get_demo("case-b")
@app.get("/api/demo/case-c")
def case_c(): return get_demo("case-c")

@app.post("/api/demo/case-b/inject-contradiction")
def inject_contradiction():
    a,b=_CASE_B; b=copy.deepcopy(b); b.infra_fingerprint="infra_CONFLICTING_CLUSTER_99"; b.infra_features=_parts(_rng,"CONFLICT")
    r=compute_actor_linkage(a,b,_WEIGHTS); audit("Contradiction detected",{"case":"case-b","signal":"infrastructure","score":r.score})
    return {"label":"Case B — Contradictory Evidence Injected","result":_serialize_result(a,b,r),"timeline":_timeline(a,b,r)}

@app.post("/api/live/investigate")
def live_investigate(payload:dict):
    if not isinstance(payload.get("original"),dict): raise HTTPException(400,"Original identity is required.")
    c=payload.get("candidates",[])
    if not isinstance(c,list) or not 2<=len(c)<=3: raise HTTPException(400,"Provide 2 or 3 candidate identities.")
    audit("Live investigation created",{"candidate_count":len(c)}); original,results=_ranked_live(payload); audit("Candidate ranking completed",{"scores":[x["result"]["score"] for x in results]})
    return {"mode":"LIVE INVESTIGATION","original":_identity_summary(original),"candidate_count":len(results),"results":results,"methodology":"Candidates are ranked by linkage strength-of-evidence, not probability of guilt."}

@app.get("/api/graph/{case}")
def graph(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    ids=[x.identity_id for x in pair]; return build_case_graph(_IDENTITIES,ids,_WEIGHTS)

@app.post("/api/live/report")
def live_report(payload:dict):
    if not isinstance(payload.get("original"),dict): raise HTTPException(400,"Original identity is required.")
    candidates=payload.get("candidates",[])
    if not isinstance(candidates,list) or not 2<=len(candidates)<=3: raise HTTPException(400,"Provide 2 or 3 candidates.")
    original,results=_ranked_live(payload)
    lines=["# Convergence Live Investigation Report",f"Generated: {datetime.utcnow().isoformat()}Z","",f"Original: `{original.identity_id}`","","## Candidate Ranking"]
    for item in results: lines.append(f"{item['rank']}. `{item['name']}` — **{item['result']['score']}/100 ({item['result']['confidence_band']})**")
    intel=results[0]["result"].get("threat_actor_intelligence",{}) if results else {}
    lines += ["","## Interpretation","Ranking reflects linkage strength-of-evidence, not probability of guilt or identity certainty.","","## Threat-Actor Intelligence Layer","Explicit PS 26151 objects represented: handles, PGP keys, wallets, trust links, marketplaces, clearnet domains, SSL certificates, certificate↔domain links, service banners, exposed server-status observations, descriptor inconsistencies, hidden-service identifiers and persona history.",f"Matched intelligence objects: **{intel.get('match_count',0)}**. This layer is corroborating evidence/context and is not a seventh score signal."]
    lines += ["","## Privacy / Anonymity Context","Tor, VPN, cryptocurrency and encrypted messaging are contextual indicators only and contribute **0** to attribution confidence.","","## Evidence / Methodology","Six attribution signals: Temporal, Account, Infrastructure, Activity, Interaction Network, Linguistic/Stylometry. Supporting evidence is combined through weighted fusion; contradictions receive a 1.5× penalty on the conflicting signal's own weight.","","## Limitation","Controlled synthetic or investigator-supplied prototype evidence does not establish real-world identity or guilt."]
    audit("Live report generated",{"candidate_count":len(results)})
    return {"report_markdown":"\n".join(lines),"ranking":results}

@app.get("/api/report/{case}")
def report(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    r=compute_actor_linkage(*pair,_WEIGHTS); audit("Report generated",{"case":case,"format":"markdown"}); return {"report_markdown":generate_report(case,*pair,r)}

@app.get("/api/report/{case}/pdf")
def report_pdf(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    r=compute_actor_linkage(*pair,_WEIGHTS); p=generate_pdf_report(case,*pair,r); return {"download_url":f"/api/report/{case}/pdf/download","filename":p.name}

@app.get("/api/report/{case}/pdf/download")
def report_pdf_download(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    r=compute_actor_linkage(*pair,_WEIGHTS); p=generate_pdf_report(case,*pair,r); audit("Report generated",{"case":case,"format":"pdf"}); return FileResponse(p,media_type="application/pdf",filename=p.name)

@app.get("/api/report/{case}/json")
def report_json(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    r=compute_actor_linkage(*pair,_WEIGHTS); return {"investigation_id":f"INV-{case.upper()}-001","original":_identity_summary(pair[0]),"candidate":_identity_summary(pair[1]),"result":_serialize_result(*pair,r),"timeline":_timeline(*pair,r)}

@app.get("/api/report/{case}/csv")
def report_csv(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    r=compute_actor_linkage(*pair,_WEIGHTS); out=io.StringIO(); w=csv.writer(out); w.writerow(["signal","similarity","weight","contribution","status","evidence_id"])
    for row in _signal_details(*pair,r): w.writerow([row["signal"],row["similarity"],row["weight"],row["contribution"],row["status"],row["provenance"]["evidence_id"]])
    return Response(out.getvalue(),media_type="text/csv",headers={"Content-Disposition":f"attachment; filename=convergence_{case}.csv"})

@app.get("/api/integrity/{case}")
def integrity(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    return {"chain":build_integrity_chain(list(pair))}

@app.post("/api/integrity/{case}/tamper-check")
def tamper(case:str):
    pair=_case(case)
    if not pair: raise HTTPException(404,"Unknown case")
    original=hash_identity_evidence(pair[0]); mutated=copy.deepcopy(pair[0]); mutated.activity_sequence=list(mutated.activity_sequence)+["TAMPERED_EVENT"]; mh=hash_identity_evidence(mutated); return {"evidence_id":original["evidence_id"],"original_sha256":original["sha256"],"mutated_sha256":mh["sha256"],"integrity":"FAILED" if original["sha256"]!=mh["sha256"] else "VERIFIED","message":"Evidence mutation detected: SHA-256 no longer matches the original evidence artifact."}

@app.get("/api/evaluation")
def evaluation(): return evaluate_on_test_set(_WEIGHTS)
@app.get("/api/weights")
def weights(): return {"weights":_WEIGHTS,"contradiction_multiplier":CONTRADICTION_MULTIPLIER,"account_decay_days":sim.ACCOUNT_DECAY_DAYS,"posting_decay_minutes":sim.POSTING_DECAY_MINUTES,"network_signal":"interaction_network","privacy_indicators_in_score":False,"threat_actor_intelligence_layer":True,"ps26151_entities":["handles","pgp_keys","wallets","trust_links","marketplaces","clearnet_domains","ssl_certificates","certificate_domain_links","service_banners","exposed_server_status","descriptor_inconsistencies","tor_services","persona_history"]}
@app.get("/api/audit")
def audit_log(): return {"entries":_AUDIT}

@app.get("/")
def root(): return {"status":"Convergence API running","attribution_signals":list(SIGNAL_LABELS.values()),"privacy_context":["Tor","VPN","Cryptocurrency","Encrypted messaging"],"privacy_context_in_score":False,"threat_actor_intelligence_layer":True,"endpoints":["/api/demo/case-a","/api/demo/case-b","/api/demo/case-c","/api/live/investigate","/api/evaluation","/api/audit"]}
