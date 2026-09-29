# Convergence — Explainable Actor-Linkage & Attribution Platform

SIH 2026 — Problem Statement 26151

## Final architecture

Investigator input → Evidence normalization → six attribution signals → evidence fusion → contradiction analysis → explainable score → confidence band → graph / progressive timeline / report → audit + SHA-256 integrity.

### Six attribution signals
1. Temporal — cosine similarity of 24-hour activity histograms + matching activity windows.
2. Account — creation timing and posting interval with configurable prototype decay parameters (`60 days`, `120 minutes`).
3. Infrastructure — exact / partial / no overlap across TLS, service/banner, certificate, server configuration and ASN-style identifiers.
4. Activity — cosine similarity of action-frequency vectors.
5. Interaction Network — behavioral interaction vector + shared counterparties.
6. Linguistic / Stylometry — cosine similarity over a **synthetic stylometric representation**.

### Context only — never in the attribution score
- Tor
- VPN
- Cryptocurrency
- Encrypted messaging

The backend enforces this separation: changing these four flags does not change the score.

## Fusion

`S_support = Σ(similarity_i × weight_i)`

Contradicting signals receive a separate negative penalty of `1.5 × the conflicting signal's own weight`, scaled by degree of conflict. The final score is clamped to `0–100`.

Confidence bands:
- 0–29 LOW
- 30–49 INCONCLUSIVE
- 50–69 MODERATE
- 70–100 STRONG

The score is strength-of-evidence, not a probability of guilt or identity certainty.

## Live investigation

Build one Original identity and 2–3 Candidates in the UI. Candidate profiles are supplied live by the investigator; the system does not silently substitute a fixed demo case. Candidates are ranked by linkage strength-of-evidence.

## Demo cases
- Case A — privacy-conscious researcher: privacy tools are present but do not raise the attribution score.
- Case B — strong multi-signal convergence; includes a contradiction-injection demo.
- Case C — mixed evidence; intentionally remains INCONCLUSIVE.

## Explainability and accountability
- Signal-level SUPPORTING / CONTRADICTING / INSUFFICIENT classification.
- Evidence IDs and provenance records with source, observation time, reliability and SHA-256 evidence hash.
- Progressive investigation timeline: evidence is incorporated sequentially and the running score can rise or fall.
- D3 correlation graph. Graph display threshold `score >= 20` is visual only, not an attribution threshold.
- SHA-256 integrity chain and tamper demonstration.
- In-memory audit trail for import, scoring, contradiction, ranking and report events.
- Markdown, PDF, JSON and CSV report endpoints.

## Evaluation

Synthetic dataset has train / validation / held-out test splits. Weights are selected by validation-based random search and then frozen before held-out evaluation. The evaluation dashboard reports Precision, Recall, F1 and FPR plus scenario-wise breakdown.

**Evaluation caveat:** controlled synthetic ground truth validates the prototype methodology; it does not establish real-world de-anonymization performance.

## Run

```bash
cd dark-web-attribution/backend
python -m pip install -r requirements.txt
python -m uvicorn api:app --reload --port 8000
```

Open `frontend/index.html` with VS Code Live Server.

API docs: `http://127.0.0.1:8000/docs`

## PS 26151 Threat-Actor Intelligence Layer

The prototype now explicitly represents the objects named in the problem statement without changing the six-signal architecture:

**Infrastructure intelligence**
- TLS / SSL certificate identifiers
- SSL-certificate ↔ clearnet-domain relationships
- clearnet domains
- service/default banners
- exposed `server-status` observations
- descriptor inconsistency markers
- server configuration / ASN-style identifiers

**Actor / persona intelligence**
- handles and aliases
- PGP key IDs
- wallet identifiers
- marketplace presence
- trust links
- hidden-service identifiers
- persona history / rebrand markers
- behavioral profiling
- explainable stylometric persona analysis

These objects are represented in the evidence model, surfaced in the UI and connected in the correlation graph. They are corroborating evidence/context and **are not silently introduced as a seventh attribution score**. Behavioral profiling and stylometry remain part of the existing Activity and Linguistic signals.

The graph can therefore show relationships such as:

`ACTOR → HANDLE → PGP KEY → WALLET → MARKETPLACE → SSL CERTIFICATE → CLEARNET DOMAIN`

and explicit `CERTIFICATE ↔ CLEARNET DOMAIN` relationships.

### Synthetic stylometry limitation

The prototype's stylometric vector is controlled/synthetic unless investigator-supplied features are entered. The similarity computation is real cosine similarity. A production implementation can replace the vector with extracted features such as sentence-length statistics, punctuation frequency, average word length, function-word frequency, vocabulary richness and character/word n-grams without changing the explainable fusion interface.

### Presentation wording

Use: **"Explainable evidence-fusion and lightweight machine-learning platform for actor linkage."**

Do not describe the prototype as proving real-world identity, as providing a probability of guilt, or as achieving a specific real-world de-anonymization accuracy. The controlled synthetic evaluation is methodological validation only.
