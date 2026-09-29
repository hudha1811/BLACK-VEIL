```markdown
# BLACK VEIL

## Uncover What Hides in the Shadows.

BLACK VEIL is an explainable Threat-Actor Attribution and Actor-Linkage Platform developed for **Smart India Hackathon (SIH) 2026 — Problem Statement 26151: Dark Web Threat Actor De-anonymization — Explainable Actor-Linkage & Attribution Platform**.

The platform correlates multiple independent behavioral, temporal, account, infrastructure, interaction, and linguistic indicators across pseudonymous identities.

The core principle of BLACK VEIL is:

> **Anonymity is not maliciousness.**

Privacy-preserving technologies such as Tor, VPNs, cryptocurrency, and encrypted messaging are treated as contextual information and **never as direct attribution evidence**.

---

# 1. Problem Statement

Threat actors may operate through multiple pseudonymous identities, accounts, services, infrastructure, and online personas.

The challenge is to determine whether apparently separate identities show meaningful evidence of being connected to the same underlying actor.

A privacy-conscious researcher may also use anonymity and privacy technologies for legitimate reasons. Therefore, the use of Tor, VPNs, cryptocurrency, or encrypted messaging cannot by itself establish maliciousness or actor linkage.

BLACK VEIL addresses this problem through an explainable evidence-convergence approach.

Instead of relying on one indicator or a black-box prediction, the system combines multiple independent evidence dimensions and produces:

- Actor-linkage score
- Confidence band
- Signal-level similarity
- Signal contribution
- Supporting evidence
- Contradicting evidence
- Evidence provenance
- Correlation graph
- Investigation timeline
- Audit information
- Investigation reports

If evidence is insufficient or contradictory, the system can return an **INCONCLUSIVE** result instead of forcing a conclusion.

---

# 2. Overall System Pipeline

The complete BLACK VEIL pipeline is:

    Raw Evidence
          ↓
    Normalization
          ↓
    Feature Extraction
          ↓
    Behavioral Fingerprinting
          ↓
    Similarity Calculation
          ↓
    Correlation Graph
          ↓
    Evidence Convergence Engine
          ↓
    Contradiction Analysis
          ↓
    Weighted Fusion
          ↓
    Actor-Linkage Score
          ↓
    Explainability + Timeline
          ↓
    Investigation Report

Each stage has a specific purpose.

### Raw Evidence

Synthetic evidence representing network, device, account, temporal, infrastructure, and optional transaction information is provided to the system.

### Normalization

Evidence from different sources is converted into a common representation.

### Feature Extraction

Useful measurable characteristics are extracted from the normalized evidence.

### Behavioral Fingerprinting

The extracted characteristics are converted into comparable fingerprints.

### Similarity Calculation

The system calculates similarity between identities for each attribution signal.

### Correlation Graph

Relationships between identities, infrastructure, evidence clusters, and intelligence entities are represented as a graph.

### Evidence Convergence

Multiple independent signals are combined.

### Contradiction Analysis

Evidence that conflicts with the proposed relationship is explicitly considered.

### Weighted Fusion

Supporting evidence is combined according to the configured signal weights.

### Actor-Linkage Score

The system produces a score from 0 to 100.

### Explainability + Timeline

The system shows why the score was produced and how evidence affected the investigation.

### Investigation Report

The investigation can be exported into structured report formats.

---

# 3. Core Principle

## Anonymity is not maliciousness.

Privacy-preserving technologies are treated only as context.

These include:

- Tor
- VPN
- Cryptocurrency
- Encrypted messaging

They do not directly contribute to attribution confidence.

Conceptually:

    Privacy / Anonymity Technology
                 ↓
          Context Only
                 ↓
       Score contribution = 0

Attribution evidence instead comes from:

- Temporal behavior
- Account behavior
- Infrastructure characteristics
- Activity behavior
- Interaction-network behavior
- Linguistic / stylometric similarity

This prevents the system from treating privacy-preserving technology itself as evidence of common ownership or maliciousness.

---

# 4. Six Primary Attribution Signals

BLACK VEIL uses six primary attribution signals:

1. Temporal
2. Account
3. Infrastructure
4. Activity
5. Interaction Network
6. Linguistic / Stylometry

These are the primary signals that contribute to the actor-linkage analysis.

---

# 5. Temporal Signal

Temporal analysis examines when identities are active.

The prototype represents activity using a 24-hour activity histogram.

For example:

    Identity A
    09:00 – 12:00
    20:00 – 22:00

    Identity B
    09:30 – 12:30
    20:00 – 22:00

The similarity between two temporal vectors is calculated using cosine similarity:

    sim_temporal = A · B / (||A|| ||B||)

A high temporal similarity can provide supporting evidence.

Temporal similarity is not considered sufficient by itself to establish attribution.

---

# 6. Account Signal

Account analysis examines account-related timing and behavior.

The prototype considers:

- Account creation timing
- Posting timing

Current prototype parameters are:

    ACCOUNT_DECAY_DAYS = 60
    POSTING_DECAY_MINUTES = 120

The calculations are:

    creation_sim = max(0, 1 - days_apart / ACCOUNT_DECAY_DAYS)

    posting_sim = max(0, 1 - minutes_diff / POSTING_DECAY_MINUTES)

    account_sim =
        0.4 * creation_sim +
        0.6 * posting_sim

These values are configurable prototype decay parameters.

They are not universal behavioral assumptions.

A production implementation would require calibration using appropriate domain-specific data.

---

# 7. Infrastructure Signal

Infrastructure analysis compares technical characteristics associated with identities or services.

The prototype can use:

- TLS fingerprints
- Service/banner information
- Certificates
- Server configuration
- ASN-style identifiers

The system can distinguish:

- Exact overlap
- Partial overlap
- No overlap

For example:

    Identity A
       |
       +--- TLS Fingerprint
       |
       +--- Certificate
       |
       +--- Service Banner

    Identity B
       |
       +--- TLS Fingerprint
       |
       +--- Certificate

Overlapping infrastructure characteristics can contribute to the overall evidence.

Infrastructure overlap is not automatically treated as proof of common ownership.

---

# 8. Activity Signal

Activity similarity compares behavioral frequency patterns.

The prototype represents activity using:

- Browse
- Post
- Message
- Upload
- Withdraw
- Login
- Search

An identity can therefore be represented as an activity vector.

Example:

    Browse      80
    Post        40
    Message     60
    Upload      20
    Withdraw    10
    Login       90
    Search      50

The vectors are compared using cosine similarity.

The interface can display the strongest matching behaviors so that the investigator can understand what produced the similarity.

---

# 9. Interaction Network Signal

Interaction-network analysis examines how identities communicate and interact with other entities.

The prototype considers:

- Shared interaction patterns
- Shared counterparties
- Similar communication structures
- Similar connection behavior

Example:

    Identity A
       ├── Counterparty X
       ├── Counterparty Y
       └── Counterparty Z

    Identity B
       ├── Counterparty X
       ├── Counterparty Y
       └── Counterparty Z

Similar interaction structures can provide supporting evidence.

These relationships can also be represented in the correlation graph.

---

# 10. Linguistic / Stylometric Signal

Linguistic analysis provides an additional evidence dimension.

Possible stylometric characteristics include:

- Function-word usage
- Sentence length
- Punctuation patterns
- Vocabulary richness
- Character n-grams
- Word n-grams
- Syntax-related characteristics

The current prototype uses a synthetic six-dimensional stylometric representation because a real linguistic corpus was not provided.

Therefore:

> The similarity computation is real; only the prototype's input stylometry is synthetic because no real corpus was provided.

This demonstrates the methodology without claiming real-world authorship attribution capability.

---

# 11. Threat-Actor Intelligence Layer

BLACK VEIL contains a Threat-Actor Intelligence Layer above the six-signal engine.

This layer provides additional contextual relationships surrounding the investigated identities.

It can represent identity intelligence such as:

- Handles
- Aliases
- PGP keys
- Wallet identifiers
- Trust links
- Marketplace presence
- Persona history
- Rebrand markers

It can also represent infrastructure intelligence such as:

- SSL/TLS certificates
- Certificate-to-domain relationships
- Service banners
- Default banners
- Exposed server-status
- Descriptor inconsistencies
- Tor service identifiers

Example relationship:

    SSL Certificate
           ↓
    Clearnet Domain
           ↓
    Service / Infrastructure
           ↓
    Pseudonymous Identity

The layer is designed to enrich investigation context and evidence relationships.

---

# 12. Threat-Actor Intelligence Is Not a Seventh Signal

The Threat-Actor Intelligence Layer does not replace or add another primary attribution signal.

The six primary signals remain:

    Temporal
    Account
    Infrastructure
    Activity
    Interaction Network
    Linguistic / Stylometry

The intelligence layer provides contextual and corroborating relationships around these signals.

Overall architecture:

    BLACK VEIL
          ↓
    Evidence Collection
          ↓
    Threat-Actor Intelligence Layer
          ↓
    ┌─────────────┬──────────────┬──────────────┐
    │             │              │
    Infrastructure Identity     Behaviour
    │             │              │
    TLS/SSL       Handles        Activity
    Certificates  PGP Keys       Temporal
    Servers       Wallets        Interaction
    Banners       Trust Links    Stylometry
    Domains       Marketplaces
    │             │              │
    └─────────────┴──────────────┘
          ↓
    Six-Signal Engine
          ↓
    Evidence Fusion
          ↓
    Score + Graph + Timeline
          ↓
    Investigation Report

---

# 13. Evidence Sources

The prototype works with synthetic evidence representing multiple source categories.

These include:

- Network
- Device
- Account
- Temporal
- Infrastructure
- Optional Transaction information

Every event is normalized into a common evidence structure.

The use of synthetic evidence allows the project to demonstrate the architecture without relying on live dark-web collection.

---

# 14. Evidence Normalization

Evidence from different sources may have different formats.

BLACK VEIL converts observations into a common normalized structure.

A normalized evidence record contains fields such as:

    {
        "evidence_id": "E-1042",
        "source": "synthetic_forum_dataset",
        "observed_at": "2026-01-15T10:30:00",
        "entity": "account_A",
        "event_type": "activity",
        "features": {},
        "reliability": 0.90,
        "hash": "SHA-256-HASH"
    }

Important fields include:

- evidence_id — unique evidence identifier
- source — source of the observation
- observed_at — observation timestamp
- entity — associated identity or entity
- event_type — evidence category
- features — extracted characteristics
- reliability — reliability value
- hash — SHA-256 integrity value

This makes evidence from different sources easier to process consistently.

---

# 15. Behavioral Fingerprinting

After normalization, useful features are extracted and converted into fingerprints.

    Temporal Fingerprint
            ↓
    24-hour activity distribution

    Account Fingerprint
            ↓
    Creation and posting behavior

    Infrastructure Fingerprint
            ↓
    TLS / certificate / service characteristics

    Activity Fingerprint
            ↓
    Browse / post / message / upload behavior

    Interaction Fingerprint
            ↓
    Counterparty and communication structure

    Linguistic Fingerprint
            ↓
    Stylometric representation

These fingerprints are then compared between identities.

---

# 16. Similarity Calculation

Each attribution signal produces an individual similarity value.

Example:

    Temporal             0.87
    Account              0.72
    Infrastructure       0.91
    Activity             0.83
    Interaction Network  0.64
    Linguistic           0.58

The individual values remain visible to the investigator.

This is important because BLACK VEIL does not hide the reasoning behind one black-box prediction.

---

# 17. Evidence Fusion

BLACK VEIL combines individual similarities using weighted evidence fusion.

Supporting evidence is calculated conceptually as:

    S_support = Σ(similarity × weight)

The final score is then adjusted using contradictory evidence:

    S_final = clamp(S_support - P_contradiction, 0, 100)

The resulting score is always between:

    0 and 100

The final score is an evidence-strength score, not a probability.

---

# 18. Weight Optimization

The project uses a validation-based weight-tuning process.

The methodology is:

    Synthetic Dataset
           ↓
    Training Data
           ↓
    Random-Search Weight Optimization
           ↓
    Validation Data
           ↓
    Best Weight Configuration
           ↓
    Freeze Weights
           ↓
    Held-Out Test

The current implementation performs approximately 300 random-search trials.

The purpose is to identify useful signal weights using validation data before evaluating the model on held-out data.

---

# 19. Contradiction Analysis

Contradictory evidence is explicitly considered.

Example:

    Temporal             SUPPORTING
    Account              SUPPORTING
    Infrastructure       SUPPORTING
    Activity              SUPPORTING
    Interaction Network  CONTRADICTING

Contradictory evidence reduces the final score.

The prototype uses a 1.5× contradiction multiplier on the conflicting signal's own weight, scaled according to the conflict degree.

The 1.5 multiplier is a prototype parameter selected through validation.

The purpose is to prevent supporting evidence from completely hiding meaningful contradictory evidence.

---

# 20. Actor-Linkage Score

BLACK VEIL produces an actor-linkage score from:

    0 – 100

The score represents the strength of available evidence under the prototype's scoring methodology.

It is not a probability.

For example:

    Score = 82

does not mean:

    82% probability that both identities belong to the same actor.

Instead, it means that the available evidence produces a score of 82 under the defined evidence-fusion methodology.

---

# 21. Confidence Bands

The prototype uses the following confidence bands:

    0–29    → LOW
    30–49   → INCONCLUSIVE
    50–69   → MODERATE
    70–100  → STRONG

These bands describe evidence strength within the prototype.

They do not represent:

- Legal attribution
- Absolute certainty
- Probability
- Proof of identity
- Proof of guilt

The system can return INCONCLUSIVE when the available evidence is insufficient.

---

# 22. Explainability

The dashboard exposes the reasoning behind the final score.

For each signal, the system can show:

- Signal
- Similarity
- Weight
- Contribution
- Status
- Observation
- Evidence ID
- Provenance

Possible statuses are:

    SUPPORTING
    CONTRADICTING
    INSUFFICIENT

Example:

    Signal: Temporal
    Similarity: 0.87
    Weight: 0.18
    Status: SUPPORTING
    Observation: Similar activity windows
    Evidence ID: E-1042

This allows the investigator to understand:

- Which signals contributed
- How strongly they contributed
- Which evidence supported the relationship
- Which evidence contradicted it
- Which evidence was insufficient

---

# 23. Correlation Graph

BLACK VEIL provides an interactive correlation graph.

Graph nodes can represent:

- Accounts
- Devices
- Infrastructure
- Evidence clusters
- Handles
- PGP keys
- Wallets
- Marketplaces
- SSL certificates
- Clearnet domains
- Service banners
- Trust links
- Tor services
- Persona history
- Descriptor inconsistencies
- Server-status information

Example:

    Account A
        │
        ├──── Temporal Similarity ──── Account B
        │
        ├──── Activity Similarity ─── Account B
        │
        ├──── Infrastructure Overlap ─ Account B
        │
        └──── Shared Counterparty ───── Account B

Every meaningful relationship should be connected to evidence.

The graph therefore provides a visual representation of the evidence network rather than an unrelated visualization.

---

# 24. Evidence Provenance

Evidence provenance allows an investigator to trace an observation back to its source.

Example:

    {
        "evidence_id": "E-1042",
        "source": "synthetic_forum_dataset",
        "observed_at": "2026-01-15T10:30:00",
        "signal": "activity",
        "value": "similar posting frequency",
        "reliability": 0.90,
        "hash": "..."
    }

This supports:

- Evidence traceability
- Reproducibility
- Investigation transparency
- Integrity checking

---

# 25. SHA-256 Integrity

BLACK VEIL supports SHA-256 hashing for evidence integrity.

The process is:

    Evidence
       ↓
    SHA-256 Hash
       ↓
    Stored Hash
       ↓
    Integrity Verification

If the evidence changes after the original hash is generated, the recalculated hash can differ.

This allows the system to detect changes to recorded evidence.

---

# 26. Investigation Timeline

The interface provides an investigation timeline showing how evidence affects the investigation.

A representative progression is:

    Evidence 1
    Account Evidence
    Score → 21

           ↓

    Evidence 2
    Temporal Evidence
    Score → 39

           ↓

    Evidence 3
    Activity Evidence
    Score → 61

           ↓

    Evidence 4
    Infrastructure Evidence
    Score → 82
    STRONG

           ↓

    Evidence 5
    Contradiction Detected
    Score → 58
    MODERATE

The timeline helps investigators understand how supporting and contradictory evidence affect the investigation.

---

# 27. Case A — Privacy-Conscious Researcher

Case A demonstrates why anonymity should not be treated as maliciousness.

The case contains privacy-preserving technologies such as:

- Tor
- VPN
- Encrypted messaging
- Cryptocurrency

However, it does not contain sufficient independent correlation between identities.

Therefore, the privacy technologies do not increase the attribution score.

The intended result demonstrates insufficient/inconclusive evidence rather than attribution based on anonymity.

This case is important because it directly demonstrates the project's ethical principle:

    Privacy-preserving technology
                 ≠
           Attribution evidence

---

# 28. Case B — Simulated Threat Actor

Case B represents a synthetic scenario containing stronger correlations.

The shared intelligence can include:

- Handles
- PGP keys
- Wallets
- Trust links
- Marketplaces
- Clearnet domains
- SSL certificates
- Certificate-domain relationships
- Service banners
- Exposed server-status
- Descriptor inconsistencies
- Tor services
- Persona history
- Rebrand markers

These relationships are combined with the six primary attribution signals.

The case demonstrates how multiple independent evidence sources can converge into a stronger actor-linkage score.

---

# 29. Case C

Case C provides an additional synthetic investigation scenario for testing evidence-convergence and explainability behavior.

The purpose of the synthetic cases is to demonstrate different evidence conditions rather than represent real-world individuals or real threat actors.

---

# 30. Live Contradiction Injection

BLACK VEIL supports a live contradiction demonstration.

A contradiction can be injected into Case B during the investigation.

The intended behavior is:

    Before contradiction
            ↓
    Higher evidence score
            ↓
    Contradiction injected
            ↓
    Evidence recalculated
            ↓
    Score decreases

The prototype demonstration can produce a lower score and confidence band after contradictory evidence is introduced.

This shows that contradictory evidence is actively incorporated into the decision process.

---

# 31. Privacy Invariance Test

The project also verifies that privacy-preserving indicators do not change attribution scores.

In the prototype, privacy-related context can be changed while the actual attribution evidence remains unchanged.

The expected behavior is:

    Base evidence score
            =
    Privacy-flipped evidence score

The current prototype produced equivalent scores for the tested configurations:

    [99.3, 98.5]

This demonstrates that privacy-context indicators do not directly affect attribution scoring.

---

# 32. Audit Log

BLACK VEIL maintains an audit trail for major investigation actions.

Examples include:

- Evidence imported
- Evidence fusion completed
- Contradiction detected
- Live investigation created
- Candidate ranking completed
- Live report generated
- Report generated

The audit log provides visibility into major investigation events.

---

# 33. Reports

BLACK VEIL can generate structured investigation reports.

Supported report formats include:

- JSON
- CSV

Reports can contain:

- Investigation information
- Candidate information
- Signal similarities
- Signal contributions
- Contradictions
- Evidence identifiers
- Provenance
- Scores
- Confidence bands

---

# 34. API Endpoints

The backend exposes the following endpoints.

## Root

    GET /

Returns information about the running API.

## Case A

    GET /api/demo/case-a

Loads the privacy-conscious researcher demonstration.

## Case B

    GET /api/demo/case-b

Loads the stronger synthetic threat-actor demonstration.

## Case C

    GET /api/demo/case-c

Loads the additional synthetic investigation scenario.

## Case B Graph

    GET /api/graph/case-b

Returns the correlation graph data for Case B.

## Evaluation

    GET /api/evaluation

Returns the synthetic evaluation results.

## Weights

    GET /api/weights

Returns the tuned signal weights.

## Audit

    GET /api/audit

Returns audit-log information.

## JSON Report

    GET /api/report/case-b/json

Returns the Case B investigation report in JSON format.

## CSV Report

    GET /api/report/case-b/csv

Returns the Case B investigation report in CSV format.

## Integrity Verification

    GET /api/integrity/case-b

Checks integrity information for Case B.

## Inject Contradiction

    POST /api/demo/case-b/inject-contradiction

Injects contradictory evidence into the Case B demonstration.

## Live Investigation

    POST /api/live/investigate

Runs a live investigation using submitted evidence.

---

# 35. Technology Stack

## Backend

The project uses:

- Python
- FastAPI
- Uvicorn
- NumPy
- NetworkX
- Pandas
- Scikit-learn
- ReportLab

The backend handles:

- Evidence processing
- Similarity calculations
- Evidence fusion
- Contradiction analysis
- Scoring
- Graph generation
- Evaluation
- Reporting
- Integrity checking
- API endpoints

## Frontend

The frontend is a web-based investigation dashboard.

It provides:

- BLACK VEIL branding
- Dark cybersecurity theme
- Case selection
- Evidence panels
- Signal analysis
- Score visualization
- Confidence bands
- Contradiction indicators
- Threat-actor intelligence
- Privacy-context indicators
- Correlation graph
- Timeline
- Audit information
- Report generation
- Live investigation controls

---

# 36. UI Theme

BLACK VEIL uses a black, red, and electric-blue cybersecurity theme.

Primary colors:

    Background       #030407
    Panels           #0A0D12
    Secondary Panels #10151D

    Electric Blue    #00A8FF
    Blue Secondary   #168BFF / #22B8FF

    Crimson          #E11D48
    Dark Crimson     #9F1239

    White            #F8FAFC
    Secondary Text   #CBD5E1
    Muted Text       #64748B

Color meaning:

    Electric Blue → Evidence / Data / Graph / Active Elements

    Crimson → Threat / Contradiction / Warning

    White → Main Text

    Black → Primary Background

The visual style is intended to resemble a serious cybersecurity investigation console.

---

# 37. Project Structure

The main project structure is:

    BLACK-VEIL/
    │
    ├── README.md
    ├── requirements.txt
    ├── .gitignore
    ├── LICENSE
    │
    ├── api.py
    │
    ├── core/
    │   ├── similarity.py
    │   ├── fingerprinting.py
    │   ├── fusion.py
    │   ├── evaluation.py
    │   └── ...
    │
    ├── tuned_weights.json
    │
    ├── frontend/
    │   └── index.html
    │
    └── reports/

The exact contents of the `core/` and `reports/` directories may evolve as the project is developed.

---

# 38. Important Files

## api.py

The main FastAPI application.

It:

- Starts the API
- Provides the project endpoints
- Loads demonstration cases
- Connects the frontend to the attribution engine
- Handles investigation requests
- Provides reports and evaluation information

## core/

Contains the core attribution logic.

The core modules handle functionality such as:

- Fingerprinting
- Similarity calculations
- Evidence fusion
- Contradiction handling
- Evaluation

## tuned_weights.json

Contains the tuned signal weights used by the prototype.

The weights are selected through the validation-based tuning process.

## frontend/index.html

Contains the BLACK VEIL investigation dashboard.

The frontend communicates with the FastAPI backend and displays:

- Cases
- Evidence
- Scores
- Graphs
- Timelines
- Threat-actor intelligence
- Reports

## reports/

Contains generated report artifacts where applicable.

---

# 39. Evaluation Methodology

The project uses synthetic data for controlled evaluation.

The evaluation flow is:

    Synthetic Dataset
           ↓
    Training Data
           ↓
    Validation
           ↓
    Weight Optimization
           ↓
    Freeze Weights
           ↓
    Held-Out Test
           ↓
    Evaluation Metrics

The system evaluates:

- Precision
- Recall
- F1 Score
- False Positive Rate
- Linkage accuracy
- Calibration-related behavior

The current evaluation setup uses a decision threshold of:

    50

for the prototype evaluation.

---

# 40. Current Synthetic Evaluation

The current prototype evaluation produced approximately:

    Precision: 0.533
    Recall:    0.800
    F1 Score:  0.640
    FPR:       0.700

The evaluation was performed on:

    20 test pairs

These results come from a controlled synthetic prototype evaluation.

They must not be interpreted as real-world de-anonymization accuracy.

For example, the result should not be described as:

    "The system is 80% accurate."

Real-world performance would require:

- Appropriate datasets
- Domain-specific calibration
- Independent testing
- Larger evaluation populations
- Realistic threat-intelligence conditions
- Appropriate ethical and legal controls

---

# 41. Why Synthetic Data Is Used

The prototype intentionally uses synthetic evidence.

Reasons include:

- Privacy
- Ethical considerations
- Reproducibility
- Demonstration safety
- Avoiding unauthorized collection
- Avoiding live dark-web surveillance

Synthetic cases allow the project to demonstrate:

    Evidence
       ↓
    Similarity
       ↓
    Fusion
       ↓
    Contradiction
       ↓
    Score
       ↓
    Explanation

without requiring real threat-actor data.

---

# 42. What BLACK VEIL Does NOT Do

BLACK VEIL is not:

- A basic Tor detector
- A maliciousness classifier
- A psychological profiler
- A live dark-web scraper
- A surveillance platform
- A black-box AI attribution system
- A system that assumes anonymity means maliciousness
- A system that claims absolute identity attribution

The platform focuses on explainable evidence correlation.

---

# 43. Ethical Design

BLACK VEIL follows several important principles.

## 1. Anonymity is not maliciousness

Using privacy-preserving technologies is not treated as evidence of malicious activity.

## 2. No single indicator is sufficient

A single matching characteristic should not automatically establish attribution.

## 3. Multiple independent evidence sources

The system looks for convergence across different evidence dimensions.

## 4. Contradictions matter

Conflicting evidence reduces the final score.

## 5. Inconclusive results are allowed

The system can return:

    INCONCLUSIVE

when evidence is insufficient.

## 6. Explainability

The system exposes how the final score was generated.

## 7. Synthetic data

The prototype explicitly uses synthetic data.

## 8. No unsupported certainty

The system does not claim absolute attribution from limited evidence.

---

# 44. Limitations

## Synthetic Data

The evaluation uses synthetic evidence rather than real-world threat-actor datasets.

## Stylometry

The current stylometric representation is synthetic.

## Prototype Parameters

Decay values, contradiction multipliers, weights, and confidence bands are prototype design parameters.

They require proper calibration for production use.

## No Live Dark-Web Scraping

The prototype does not perform live dark-web surveillance or automated collection of real threat-actor information.

## Attribution Is Evidence-Based, Not Absolute

A high score represents strong evidence under the model.

It does not guarantee that two identities belong to the same real-world person or organization.

---

# 45. Future Scope

Possible future improvements include:

- Larger validated datasets
- Real-world calibrated parameters
- More advanced stylometric analysis
- Additional graph analytics
- Improved score calibration
- More sophisticated anomaly detection
- Advanced machine-learning components
- Richer timeline analysis
- More detailed evidence provenance
- Domain-specific threat-intelligence integrations
- Improved graph visualization
- Expanded investigation workflows

Any future real-world deployment would require appropriate legal, ethical, privacy, and security controls.

---

# 46. Suggested Demo Flow

A complete demonstration can follow this sequence:

    1. Open BLACK VEIL

    2. Select Case A

    3. Show:
       Tor
       VPN
       Cryptocurrency
       Encrypted Messaging

    4. Demonstrate:
       Privacy Context
       Score Contribution = 0

    5. Select Case B

    6. Show:
       Temporal Similarity
       Account Similarity
       Activity Similarity
       Infrastructure Similarity
       Interaction Similarity
       Linguistic Similarity

    7. Show:
       Threat-Actor Intelligence

    8. Open:
       Correlation Graph

    9. Select graph relationships

    10. Show:
        Evidence IDs
        Provenance
        Signal Contribution

    11. Open:
        Investigation Timeline

    12. Inject Contradiction

    13. Show:
        Score Reduction

    14. Open:
        Evaluation

    15. Generate:
        JSON / CSV Report

This demonstrates the complete evidence-convergence workflow.

---

# 47. Installation

## Requirements

Install Python 3.x.

The project dependencies are listed in:

    requirements.txt

Install them using:

    python -m pip install -r requirements.txt

For the Python installation used during development:

    C:\Python314\python.exe -m pip install -r requirements.txt

---

# 48. Running the Backend

Open a terminal inside the project directory.

Run:

    C:\Python314\python.exe -m uvicorn api:app --reload

The backend should start at:

    http://127.0.0.1:8000

A successful startup should show something similar to:

    Uvicorn running on http://127.0.0.1:8000
    Application startup complete.

Keep this terminal running while using the frontend.

---

# 49. Running the Frontend

After starting the backend, open:

    frontend/index.html

in a web browser.

The frontend communicates with:

    http://127.0.0.1:8000

Do not close the backend terminal while using the dashboard.

---

# 50. Quick Start

From the project directory:

    cd path\to\BLACK-VEIL

    C:\Python314\python.exe -m pip install -r requirements.txt

    C:\Python314\python.exe -m uvicorn api:app --reload

Then open:

    http://127.0.0.1:8000

and open:

    frontend/index.html

---

# 51. Backend Verification

After starting the backend, open:

    http://127.0.0.1:8000

The API should return information similar to:

    {
        "status": "Convergence API running",
        "attribution_signals": [
            "Temporal",
            "Account",
            "Infrastructure",
            "Activity",
            "Interaction Network",
            "Linguistic / Stylometry"
        ],
        "privacy_context": [
            "Tor",
            "VPN",
            "Cryptocurrency",
            "Encrypted messaging"
        ],
        "privacy_context_in_score": false,
        "threat_actor_intelligence_layer": true
    }

This confirms that the FastAPI backend is running.

---

# 52. Development Verification

The Python modules can be syntax-checked using:

    C:\Python314\python.exe -m py_compile api.py core/*.py

If the command completes successfully, the checked Python files compile without syntax errors.

---

# 53. Key Features

BLACK VEIL provides:

    ✓ Six-signal actor-linkage analysis

    ✓ Temporal similarity

    ✓ Account similarity

    ✓ Infrastructure similarity

    ✓ Activity similarity

    ✓ Interaction-network similarity

    ✓ Linguistic / stylometric similarity

    ✓ Threat-actor intelligence layer

    ✓ Privacy-preserving context separation

    ✓ Evidence normalization

    ✓ Behavioral fingerprinting

    ✓ Weighted evidence fusion

    ✓ Contradiction analysis

    ✓ Explainable actor-linkage score

    ✓ Confidence bands

    ✓ Correlation graph

    ✓ Evidence provenance

    ✓ SHA-256 integrity checking

    ✓ Investigation timeline

    ✓ Audit log

    ✓ Synthetic Case A

    ✓ Synthetic Case B

    ✓ Synthetic Case C

    ✓ Live contradiction injection

    ✓ Synthetic evaluation

    ✓ JSON reports

    ✓ CSV reports

    ✓ FastAPI backend

    ✓ Interactive investigation dashboard

---

# 54. Final Architecture

    ┌──────────────────────────────────────┐
    │              BLACK VEIL              │
    │     Explainable Actor-Linkage       │
    │             Platform                 │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │          Evidence Sources            │
    │ Network / Device / Account           │
    │ Temporal / Infrastructure            │
    │ Optional Transaction                 │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │       Evidence Normalization         │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │        Feature Extraction            │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │      Behavioral Fingerprinting       │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │          SIX-SIGNAL ENGINE           │
    │                                      │
    │ Temporal                             │
    │ Account                              │
    │ Infrastructure                      │
    │ Activity                             │
    │ Interaction Network                 │
    │ Linguistic / Stylometry             │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │   Threat-Actor Intelligence Layer    │
    │                                      │
    │ Handles / PGP / Wallets              │
    │ Certificates / Domains               │
    │ Banners / Trust / Persona            │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │       Similarity Calculation         │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │          Evidence Fusion             │
    └──────────────────┬───────────────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
       Supporting          Contradicting
        Evidence             Evidence
              │                 │
              └────────┬────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │        Actor-Linkage Score           │
    │              0 – 100                 │
    └──────────────────┬───────────────────┘
                       │
             ┌─────────┼─────────┐
             │         │         │
             ▼         ▼         ▼
       Explainability Graph   Timeline
             │         │         │
             └─────────┼─────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │       Investigation Report           │
    │             JSON / CSV               │
    └──────────────────────────────────────┘

---

# 55. Project Objective

The objective of BLACK VEIL is not to blindly identify anonymous users.

The objective is to provide an explainable framework that allows investigators to examine whether multiple pseudonymous identities show meaningful convergence across independent evidence dimensions.

The overall reasoning model is:

    Evidence
       +
    Independent Signals
       +
    Similarity
       +
    Contradiction Analysis
       +
    Provenance
       +
    Explainability
       ↓
    Evidence-Based Actor Linkage

while maintaining the core principle:

    Privacy ≠ Maliciousness

---

# 56. Conclusion

BLACK VEIL demonstrates an explainable approach to threat-actor actor-linkage by combining:

- Behavioral evidence
- Temporal evidence
- Account evidence
- Infrastructure evidence
- Interaction-network evidence
- Linguistic/stylometric evidence
- Threat-actor intelligence
- Evidence provenance
- Contradiction analysis
- Graph relationships
- Timeline analysis
- Integrity verification

Instead of relying on a black-box prediction, the platform exposes:

- What evidence was observed
- Which signals matched
- Which signals contradicted
- How much each signal contributed
- Where the evidence came from
- How graph relationships were formed
- How the score changed during the investigation
- Why the final confidence band was reached

The project is a research/prototype implementation using synthetic evidence and controlled evaluation.

Its central principle remains:

> **Uncover What Hides in the Shadows — without treating privacy itself as evidence of wrongdoing.**

---


Refer to the project's LICENSE file for the applicable license terms.
```
