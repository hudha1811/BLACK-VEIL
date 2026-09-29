# 🕶️ BLACK VEIL

## Uncover What Hides in the Shadows.

**BLACK VEIL** is an explainable **Threat-Actor Attribution and Actor-Linkage Platform** developed for **Smart India Hackathon (SIH) 2026**, addressing:

> **Problem Statement 26151 — Dark Web Threat Actor De-anonymization — Explainable Actor-Linkage & Attribution Platform**

BLACK VEIL is designed to analyze multiple independent evidence sources and identify whether different pseudonymous identities show meaningful similarities that may indicate a potential relationship.

Instead of relying on a black-box AI prediction or a single suspicious indicator, BLACK VEIL combines **temporal, account, infrastructure, activity, interaction-network, and linguistic evidence** and presents the reasoning behind the resulting actor-linkage score.

The platform is designed around one important principle:

> **Anonymity is not maliciousness.**

The use of privacy-preserving technologies such as Tor, VPNs, cryptocurrency, or encrypted messaging is treated only as contextual information and does **not** directly increase the attribution score.

---

## 🎯 Problem Statement

Threat actors may operate using multiple pseudonymous accounts, services, infrastructure, communication identities, and online personas.

This creates a difficult investigation problem:

**How can investigators determine whether multiple pseudonymous identities may be connected to the same actor without relying on a single indicator or assuming that anonymity itself is suspicious?**

A useful attribution system needs to correlate multiple independent forms of evidence while also considering contradictory evidence.

BLACK VEIL addresses this through an explainable evidence-correlation pipeline:

```text
Raw Evidence
     ↓
Evidence Normalization
     ↓
Feature Extraction
     ↓
Behavioral Fingerprinting
     ↓
Similarity Calculation
     ↓
Correlation Graph
     ↓
Evidence Convergence
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
