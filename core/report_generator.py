"""Markdown/PDF investigation report generation."""
from datetime import datetime
from pathlib import Path
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from .synthetic_data import Identity
from .convergence_engine import ConvergenceResult
from .integrity import hash_identity_evidence
from . import similarity as sim

def _signals(a,b,result):
    funcs={"temporal":sim.temporal_similarity,"account":sim.account_similarity,"infrastructure":sim.infrastructure_similarity,"activity":sim.activity_similarity,"interaction_network":sim.interaction_network_similarity,"linguistic":sim.linguistic_similarity}
    rows=[]
    for s,fn in funcs.items():
        v,d=fn(a,b); status="CONTRADICTING" if s in result.contradictory_evidence else "SUPPORTING" if s in result.supporting_evidence else "INSUFFICIENT"; rows.append((s,v,result.contributions[s],status,f"E-{a.identity_id}-{b.identity_id}-{s}"))
    return rows

def generate_report(case_id,a,b,result):
    lines=[f"# Convergence Investigation Report — {case_id}",f"Generated: {datetime.utcnow().isoformat()}Z","","## Investigation Identities",f"- Original: `{a.identity_id}`",f"- Candidate: `{b.identity_id}`","","## Linkage Strength-of-Evidence",f"**{result.score}/100 — {result.confidence_band}**","","> This score represents strength of evidence. It is not a probability of guilt, identity certainty, or a declaration of real-world identity.","","## Signal Breakdown"]
    for s,v,c,status,eid in _signals(a,b,result): lines.append(f"- **{s}** — similarity `{v:.3f}`; contribution `{c:+.2f}`; status **{status}**; Evidence ID `{eid}`")
    lines += ["","## Supporting Evidence"] + ([f"- {k}: {v}" for k,v in result.supporting_evidence.items()] or ["- None."]) + ["","## Contradicting Evidence"] + ([f"- {k}: {v}" for k,v in result.contradictory_evidence.items()] or ["- None detected."]) + ["","## Insufficient Evidence"] + ([f"- {k}: {v}" for k,v in result.insufficient_evidence.items()] or ["- None."]) 
    intel=sim.threat_actor_intelligence(a,b)
    lines += ["","## Threat-Actor Intelligence Layer",f"- Shared intelligence objects: **{intel['match_count']}**",f"- Handles: `{intel['matches']['handles']}`",f"- PGP keys: `{intel['matches']['pgp_keys']}`",f"- Wallets: `{intel['matches']['wallets']}`",f"- Trust links: `{intel['matches']['trust_links']}`",f"- Marketplaces: `{intel['matches']['marketplaces']}`",f"- Clearnet domains: `{intel['matches']['clearnet_domains']}`",f"- SSL certificates: `{intel['matches']['ssl_certificates']}`",f"- Certificate ↔ domain links: `{intel['shared_certificate_domain_links']}`",f"- Service/default banners: `{intel['matches']['service_banners']}`",f"- Exposed server-status: `{intel['matches']['exposed_server_status']}`",f"- Descriptor inconsistencies: `{intel['matches']['descriptor_inconsistencies']}`",f"- Hidden-service identifiers: `{intel['matches']['tor_services']}`",f"- Persona history overlap: `{intel['persona_history_overlap']}`", "- This layer is explicit corroborating context and is not a seventh score signal.","","## Privacy / Anonymity Context — NOT Attribution Evidence",f"- Original: `{result.privacy_context['identity_a']}`",f"- Candidate: `{result.privacy_context['identity_b']}`","- Tor, VPN, cryptocurrency and encrypted messaging do not contribute to the score.","","## Methodology","- Temporal: 24-hour activity histogram cosine similarity + matching activity windows.",f"- Account: 0.4 × creation similarity + 0.6 × posting-interval similarity; decay parameters: {sim.ACCOUNT_DECAY_DAYS} days and {sim.POSTING_DECAY_MINUTES} minutes.","- Infrastructure: exact / partial / no component overlap across TLS, service, certificate, server and ASN-style identifiers.","- Activity: action-frequency vector cosine similarity.","- Interaction Network: interaction-behavior vector and shared counterparties.","- Linguistic: cosine similarity over a synthetic stylometric representation.","- Fusion: Σ(similarity × weight), with contradiction penalty applied separately.","- Contradiction multiplier: 1.5× the conflicting signal's own weight; selected/tuned for the controlled prototype.","- Confidence: 0–29 LOW; 30–49 INCONCLUSIVE; 50–69 MODERATE; 70–100 STRONG.","","## Investigation Timeline","Evidence is incorporated sequentially; the running score can increase or decrease as evidence arrives."]
    for i in _signals(a,b,result): pass
    lines += ["","## Evidence Integrity"]
    for x in (a,b):
        h=hash_identity_evidence(x); lines.append(f"- `{h['evidence_id']}` — SHA-256 `{h['sha256']}`")
    lines += ["","## Limitations","This prototype uses controlled synthetic evidence and synthetic ground truth. Evaluation results are methodological validation only and do not establish real-world de-anonymization performance.","","## Decision-Support Notice","This report is decision-support output. It does not establish real-world identity or guilt."]
    return "\n".join(lines)

def generate_pdf_report(case_id,a,b,result):
    out=Path(__file__).resolve().parents[2]/"generated_reports"; out.mkdir(exist_ok=True); path=out/f"investigation_report_{case_id}.pdf"
    styles=getSampleStyleSheet(); body=ParagraphStyle("body",parent=styles["BodyText"],fontSize=8.5,leading=12); small=ParagraphStyle("small",parent=body,fontSize=7,textColor=colors.grey); head=ParagraphStyle("head",parent=styles["Heading2"],fontSize=11,spaceBefore=8,spaceAfter=5)
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=14*mm,bottomMargin=14*mm)
    story=[Paragraph(f"Convergence Investigation Report — {escape(case_id)}",styles["Title"]),Paragraph(f"Generated: {datetime.utcnow().isoformat()}Z",small),Paragraph("Investigation Identities",head),Paragraph(f"Original: <b>{escape(a.identity_id)}</b><br/>Candidate: <b>{escape(b.identity_id)}</b>",body),Paragraph("Linkage Strength-of-Evidence",head),Paragraph(f"<b>{result.score}/100 — {result.confidence_band}</b>",body),Paragraph("This score represents strength of evidence, not probability of guilt or identity certainty.",small),Paragraph("Signal Breakdown",head)]
    rows=[["Signal","Similarity","Contribution","Status","Evidence ID"]]
    for s,v,c,status,eid in _signals(a,b,result): rows.append([s,f"{v:.3f}",f"{c:+.2f}",status,eid])
    t=Table(rows,colWidths=[32*mm,25*mm,28*mm,28*mm,67*mm]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.3,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),6.5),("VALIGN",(0,0),(-1,-1),"TOP")])); story += [t,Spacer(1,6)]
    for title,e in [("Supporting Evidence",result.supporting_evidence),("Contradicting Evidence",result.contradictory_evidence),("Insufficient Evidence",result.insufficient_evidence)]:
        story.append(Paragraph(title,head)); story.extend([Paragraph(f"<b>{escape(k)}</b>: {escape(str(v))}",body) for k,v in e.items()] or [Paragraph("None identified.",body)])
    intel=sim.threat_actor_intelligence(a,b)
    story += [Paragraph("Threat-Actor Intelligence Layer",head),Paragraph(f"Shared objects: <b>{intel['match_count']}</b><br/>Handles: {escape(str(intel['matches']['handles']))}<br/>PGP keys: {escape(str(intel['matches']['pgp_keys']))}<br/>Wallets: {escape(str(intel['matches']['wallets']))}<br/>Trust links: {escape(str(intel['matches']['trust_links']))}<br/>Marketplaces: {escape(str(intel['matches']['marketplaces']))}<br/>Clearnet domains: {escape(str(intel['matches']['clearnet_domains']))}<br/>SSL certificates: {escape(str(intel['matches']['ssl_certificates']))}<br/>Certificate ↔ domain links: {escape(str(intel['shared_certificate_domain_links']))}<br/>Service/default banners: {escape(str(intel['matches']['service_banners']))}<br/>Exposed server-status: {escape(str(intel['matches']['exposed_server_status']))}<br/>Descriptor inconsistencies: {escape(str(intel['matches']['descriptor_inconsistencies']))}<br/>Hidden-service identifiers: {escape(str(intel['matches']['tor_services']))}<br/>Persona history overlap: {escape(str(intel['persona_history_overlap']))}<br/>This layer is corroborating context and is not a seventh score signal.",body),Paragraph("Privacy / Anonymity Context — NOT Attribution Evidence",head),Paragraph(f"Original: {escape(str(result.privacy_context['identity_a']))}<br/>Candidate: {escape(str(result.privacy_context['identity_b']))}<br/>These indicators do not contribute to the attribution score.",body),Paragraph("Methodology",head),Paragraph("Temporal cosine similarity; configurable account decay; infrastructure component overlap; activity cosine similarity; interaction-network similarity; synthetic stylometry; weighted evidence fusion; separate contradiction penalty; confidence bands.",body),Paragraph("Evidence Integrity",head)]
    for x in (a,b):
        h=hash_identity_evidence(x); story.append(Paragraph(f"{h['evidence_id']} — SHA-256: {h['sha256']}",small))
    story += [Paragraph("Limitations",head),Paragraph("Controlled synthetic evaluation only. It does not establish real-world de-anonymization performance.",body),Paragraph("Decision-Support Notice: This report does not establish real-world identity or guilt.",small)]
    doc.build(story); return path
