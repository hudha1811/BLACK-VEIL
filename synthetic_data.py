"""Controlled synthetic evidence generator for the Convergence prototype."""
import random, hashlib, json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import List, Dict

ACTION_TYPES = ["browse", "post", "message", "upload", "withdraw", "login", "search"]
INFRA_KEYS = ["tls", "service", "certificate", "server", "asn"]
INTEL_ENTITY_TYPES = ["handle", "pgp_key", "wallet", "trust_link", "marketplace", "clearnet_domain", "ssl_certificate", "service_banner", "server_status", "descriptor_inconsistency", "tor_service", "persona_history"]

@dataclass
class Identity:
    identity_id: str
    actor_id: str
    active_hours: List[int]
    session_gap_minutes: float
    infra_fingerprint: str
    account_creation_ts: datetime
    posting_interval_minutes: float
    activity_sequence: List[str]
    uses_tor: bool
    uses_vpn: bool
    uses_crypto: bool
    uses_encrypted_msg: bool
    writing_style_vector: List[float]
    scenario_type: str
    interaction_vector: List[float] = field(default_factory=lambda: [0.0] * 5)
    interaction_counterparties: List[str] = field(default_factory=list)
    infra_features: Dict[str, str] = field(default_factory=dict)
    # Threat-Actor Intelligence Layer: explicit PS 26151 entities.
    handles: List[str] = field(default_factory=list)
    pgp_keys: List[str] = field(default_factory=list)
    wallets: List[str] = field(default_factory=list)
    trust_links: List[str] = field(default_factory=list)
    marketplaces: List[str] = field(default_factory=list)
    clearnet_domains: List[str] = field(default_factory=list)
    ssl_certificates: List[str] = field(default_factory=list)
    certificate_domain_links: List[Dict[str, str]] = field(default_factory=list)
    service_banners: List[str] = field(default_factory=list)
    exposed_server_status: List[str] = field(default_factory=list)
    descriptor_inconsistencies: List[str] = field(default_factory=list)
    tor_services: List[str] = field(default_factory=list)
    persona_history: List[str] = field(default_factory=list)

    def evidence_hash(self) -> str:
        payload = json.dumps(asdict(self), default=str, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

@dataclass
class IdentityPair:
    id_a: str
    id_b: str
    ground_truth_linked: bool
    scenario_type: str


def _jitter_hours(base_hours, spread, noise, rng):
    out=[]
    for h in base_hours:
        for _ in range(rng.randint(3,8)):
            nh=int(round(h+rng.gauss(0,spread)))%24
            if rng.random()<noise: nh=rng.randint(0,23)
            out.append(nh)
    return out


def _infra_parts(seed: str, rng: random.Random, shared_parts=None):
    if shared_parts is not None:
        return dict(shared_parts)
    return {
        "tls": f"tls_{rng.randint(1,5)}",
        "service": f"svc_{rng.randint(1,7)}",
        "certificate": f"cert_{rng.randint(1,10)}",
        "server": f"srv_{rng.randint(1,8)}",
        "asn": f"asn_{rng.randint(1,12)}",
    }


def _make_identity(identity_id, actor_id, scenario_type, base_hours, infra, style_seed, rng,
                   hour_spread=1.0, noise=0.05, privacy_tools=False,
                   interaction_seed=None, infra_features=None):
    creation_ts=datetime(2026,1,1)+timedelta(days=rng.randint(0,200),hours=rng.randint(0,23))
    style=[round(s+rng.gauss(0,0.05),4) for s in style_seed]
    if interaction_seed is None:
        interaction=[round(max(0.0,rng.gauss(10,3)),3) for _ in range(5)]
    else:
        interaction=[round(max(0.0,x+rng.gauss(0,0.7)),3) for x in interaction_seed]
    parts=infra_features or _infra_parts(infra,rng)
    intel=_default_intelligence(identity_id, actor_id, parts, rng)
    return Identity(
        identity_id=identity_id, actor_id=actor_id,
        active_hours=_jitter_hours(base_hours,hour_spread,noise,rng),
        session_gap_minutes=max(1.0,rng.gauss(45,15)),
        infra_fingerprint=infra,
        account_creation_ts=creation_ts,
        posting_interval_minutes=max(1.0,rng.gauss(120,40)),
        activity_sequence=[rng.choice(ACTION_TYPES) for _ in range(rng.randint(15,40))],
        uses_tor=privacy_tools or rng.random()<0.3,
        uses_vpn=privacy_tools or rng.random()<0.4,
        uses_crypto=privacy_tools or rng.random()<0.3,
        uses_encrypted_msg=privacy_tools or rng.random()<0.5,
        writing_style_vector=style, scenario_type=scenario_type,
        interaction_vector=interaction,
        interaction_counterparties=[f"cp_{rng.randint(1,20)}" for _ in range(rng.randint(2,5))],
        infra_features=parts,
        **intel,
    )


def _default_intelligence(identity_id, actor_id, infra_features, rng):
    """Generate explicit, linked synthetic intelligence objects for PS 26151."""
    tag = actor_id.replace(" ", "_")
    handle = identity_id.replace("_A", "").replace("_B", "")
    cert = (infra_features or {}).get("certificate", f"cert_{rng.randint(1,10)}")
    domain = f"{tag}.example"
    marketplace = f"market_{rng.randint(1,4)}"
    return {
        "handles": [handle],
        "pgp_keys": [f"PGP_{tag.upper()}_{rng.randint(100,999)}"],
        "wallets": [f"WALLET_{tag.upper()}_{rng.randint(100,999)}"],
        "trust_links": [f"TRUST_{tag}_{rng.randint(1,5)}"],
        "marketplaces": [marketplace],
        "clearnet_domains": [domain],
        "ssl_certificates": [cert],
        "certificate_domain_links": [{"certificate": cert, "domain": domain}],
        "service_banners": [(infra_features or {}).get("service", f"svc_{rng.randint(1,7)}")],
        "exposed_server_status": [],
        "descriptor_inconsistencies": [],
        "tor_services": [f"onion_{tag}_{rng.randint(100,999)}"],
        "persona_history": [f"{handle}:initial_persona"]
    }


def generate_dataset(n_scenarios_per_type=25, seed=42):
    rng=random.Random(seed); identities=[]; pairs=[]
    def new_style(): return [rng.uniform(0,1) for _ in range(6)]
    for i in range(n_scenarios_per_type):
        actor=f"privacy_user_{i}"
        identities.append(_make_identity(f"{actor}_A",actor,"legitimate_privacy_user",[rng.randint(0,23)],f"infra_{rng.randint(1,50)}",new_style(),rng,privacy_tools=True))

        ax,ay=f"unrelated_X_{i}",f"unrelated_Y_{i}"
        x=_make_identity(f"{ax}_A",ax,"independent_unrelated_users",[20,21],f"infra_{rng.randint(1,50)}",new_style(),rng)
        y=_make_identity(f"{ay}_A",ay,"independent_unrelated_users",[20,21],f"infra_{rng.randint(1,50)}",new_style(),rng)
        identities += [x,y]; pairs.append(IdentityPair(x.identity_id,y.identity_id,False,"independent_unrelated_users"))

        actor_s=f"same_actor_{i}"; hours=[rng.randint(0,23),rng.randint(0,23)]; infra=f"infra_{rng.randint(1,50)}"; style=new_style(); iv=[rng.uniform(5,20) for _ in range(5)]
        parts=_infra_parts(infra,rng)
        s1=_make_identity(f"{actor_s}_A",actor_s,"same_actor_multi_identity",hours,infra,style,rng,.7,.03,False,iv,parts)
        s2=_make_identity(f"{actor_s}_B",actor_s,"same_actor_multi_identity",hours,infra,style,rng,.7,.03,False,iv,parts)
        identities += [s1,s2]; pairs.append(IdentityPair(s1.identity_id,s2.identity_id,True,"same_actor_multi_identity"))

        actor_p=f"partial_{i}"; p1=_make_identity(f"{actor_p}_A",actor_p,"partial_overlap",[rng.randint(0,23)],f"infra_{rng.randint(1,50)}",new_style(),rng)
        p2=_make_identity(f"{actor_p}_B",actor_p,"partial_overlap",p1.active_hours[:2] or [12],f"infra_{rng.randint(1,50)}",new_style(),rng)
        identities += [p1,p2]; pairs.append(IdentityPair(p1.identity_id,p2.identity_id,False,"partial_overlap"))

        actor_c=f"contradict_{i}"; hours_c=[rng.randint(0,23)]; style_c=new_style(); ivc=[rng.uniform(5,20) for _ in range(5)]
        parts1=_infra_parts("c1",rng); parts2=_infra_parts("c2",rng)
        c1=_make_identity(f"{actor_c}_A",actor_c,"contradictory_evidence",hours_c,"infra_FIXED_1",style_c,rng,.5,.02,False,ivc,parts1)
        c2=_make_identity(f"{actor_c}_B",actor_c,"contradictory_evidence",hours_c,"infra_FIXED_2_CONFLICT",style_c,rng,.5,.02,False,ivc,parts2)
        identities += [c1,c2]; pairs.append(IdentityPair(c1.identity_id,c2.identity_id,True,"contradictory_evidence"))

        actor_n=f"noisy_{i}"; hn=[rng.randint(0,23),rng.randint(0,23)]; infran=f"infra_{rng.randint(1,50)}"; stylen=new_style(); ivn=[rng.uniform(5,20) for _ in range(5)]; partsn=_infra_parts(infran,rng)
        n1=_make_identity(f"{actor_n}_A",actor_n,"noisy_behavioral",hn,infran,stylen,rng,3.0,.25,False,ivn,partsn)
        n2=_make_identity(f"{actor_n}_B",actor_n,"noisy_behavioral",hn,infran,stylen,rng,3.0,.25,False,ivn,partsn)
        identities += [n1,n2]; pairs.append(IdentityPair(n1.identity_id,n2.identity_id,True,"noisy_behavioral"))
    rng.shuffle(pairs); n=len(pairs); train_end=int(n*.6); val_end=int(n*.8)
    return {"identities":{x.identity_id:x for x in identities},"pairs":{"train":pairs[:train_end],"val":pairs[train_end:val_end],"test":pairs[val_end:]}}
