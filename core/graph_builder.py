"""PS-specific evidence-linked NetworkX graph builder."""
import networkx as nx
from .convergence_engine import compute_actor_linkage
from . import similarity as sim

ENTITY_FIELDS = {
    "handles":"HANDLE", "pgp_keys":"PGP KEY", "wallets":"WALLET", "trust_links":"TRUST LINK",
    "marketplaces":"MARKETPLACE", "clearnet_domains":"CLEARNET DOMAIN", "ssl_certificates":"SSL CERTIFICATE",
    "service_banners":"SERVICE BANNER", "exposed_server_status":"SERVER-STATUS",
    "descriptor_inconsistencies":"DESCRIPTOR INCONSISTENCY", "tor_services":"TOR SERVICE", "persona_history":"PERSONA HISTORY"
}

def build_case_graph(identities,identity_ids,weights=None):
    G=nx.Graph(); edges=[]
    for iid in identity_ids:
        i=identities[iid]; G.add_node(iid,node_type="identity",scenario_type=i.scenario_type,uses_tor=i.uses_tor,uses_vpn=i.uses_vpn)
        for field,label in ENTITY_FIELDS.items():
            for value in (getattr(i,field,[]) or []):
                node_id=f"{label}:{value}"
                G.add_node(node_id,node_type="evidence",entity_type=label,value=value)
                G.add_edge(iid,node_id,edge_type="evidence_entity",entity_type=label,relationship="observed association",score=0)
        for link in (getattr(i,"certificate_domain_links",[]) or []):
            cert=f"SSL CERTIFICATE:{link.get('certificate')}"; domain=f"CLEARNET DOMAIN:{link.get('domain')}"
            if cert in G and domain in G:
                G.add_edge(cert,domain,edge_type="certificate_domain_link",entity_type="SSL ↔ CLEARNET",relationship="certificate tied to clearnet domain",score=0)
    # Identity-to-identity convergence edges retain the six-signal score and provenance.
    for i in range(len(identity_ids)):
        for j in range(i+1,len(identity_ids)):
            a,b=identities[identity_ids[i]],identities[identity_ids[j]]; r=compute_actor_linkage(a,b,weights)
            if r.score>=20:
                details=[]
                for sig,fn in [("temporal",sim.temporal_similarity),("activity",sim.activity_similarity),("interaction_network",sim.interaction_network_similarity),("infrastructure",sim.infrastructure_similarity)]:
                    v,d=fn(a,b); details.append({"signal":sig,"similarity":round(v,3),"detail":d})
                G.add_edge(a.identity_id,b.identity_id,edge_type="identity_linkage",score=r.score,band=r.confidence_band,confidence_band=r.confidence_band)
                edges.append({"source":a.identity_id,"target":b.identity_id,"score":r.score,"confidence_band":r.confidence_band,"edge_type":"identity_linkage","evidence_threshold_note":"20 is a graph-display threshold, not an attribution threshold","evidence":details,"supporting_evidence":r.supporting_evidence,"contradictory_evidence":r.contradictory_evidence,"threat_actor_intelligence":sim.threat_actor_intelligence(a,b)})
    # Serialize every graph edge, including evidence entities.
    for u,v,d in G.edges(data=True):
        if d.get("edge_type") != "identity_linkage":
            edges.append({"source":u,"target":v,**d})
    return {"nodes":[{"id":n,**G.nodes[n]} for n in G.nodes],"edges":edges}
