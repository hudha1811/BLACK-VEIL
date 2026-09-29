"""
Evidence Integrity / Audit Trail
=================================
Each evidence artifact gets a SHA-256 hash + timestamp, forming a
tamper-evident chain. This demonstrates integrity/tamper-detection —
it does NOT by itself establish legal admissibility (stated explicitly
in the report output, per the frozen ethical positioning).
"""

import hashlib
import json
import time
from typing import Dict, List
from .synthetic_data import Identity


def hash_identity_evidence(identity: Identity) -> Dict:
    h = identity.evidence_hash()
    return {
        "evidence_id": f"E-{identity.identity_id}",
        "sha256": h,
        "timestamp": time.time(),
        "source": identity.identity_id,
        "note": "Hash demonstrates tamper-evidence, not legal admissibility.",
    }


def build_integrity_chain(identities: List[Identity]) -> List[Dict]:
    return [hash_identity_evidence(i) for i in identities]
