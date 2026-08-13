"""
Enterprise Intelligence — Trust Receipt

Purpose
-------
Build a canonical, cryptographically identifiable Trust Receipt for an
enterprise decision.

The Trust Receipt connects:

    Evidence
        +
    AI findings
        +
    Enterprise policy
        +
    Authorization context
        +
    Execution context
        ↓
    Canonical Trust Receipt
        ↓
    Cryptographic Commitment

Important security boundary
---------------------------
The Trust Receipt may contain sensitive enterprise information.

This module therefore supports two concepts:

1. A complete protected receipt payload.
2. A cryptographic commitment to that canonical payload.

The complete receipt should be encrypted and stored in protected enterprise
storage. The cryptographic commitment can be anchored on-chain.

This module does NOT:
- encrypt the receipt itself;
- manage encryption keys;
- upload receipt data to storage;
- sign Smart Account transactions;
- write directly to the blockchain.

Those responsibilities belong to the deployment/application layer.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TrustReceiptError(Exception):
    """Base exception for Trust Receipt errors."""


class TrustReceiptValidationError(TrustReceiptError):
    """Raised when a Trust Receipt payload is invalid."""


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def utc_now() -> str:
    """Return the current UTC time as an ISO-8601 string."""

    return datetime.now(timezone.utc).isoformat()


def canonicalize(payload: Mapping[str, Any]) -> str:
    """
    Convert a receipt payload into deterministic JSON.

    Stable ordering is essential because the resulting representation is
    used to generate a cryptographic commitment.
    """

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def calculate_commitment(payload: Mapping[str, Any]) -> str:
    """
    Calculate a SHA-256 commitment over the canonical receipt payload.

    The 0x prefix makes the result convenient to display alongside
    blockchain-oriented hashes.
    """

    canonical = canonicalize(payload)

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"0x{digest}"


def verify_commitment(
    payload: Mapping[str, Any],
    expected_commitment: str,
) -> bool:
    """
    Verify that a payload matches a previously recorded commitment.
    """

    return calculate_commitment(payload).lower() == (
        expected_commitment.lower()
    )


# ---------------------------------------------------------------------------
# Trust Receipt model
# ---------------------------------------------------------------------------

@dataclass
class TrustReceipt:
    """
    Structured Trust Receipt.

    `payload` is the complete protected decision record.

    `receipt_commitment` is the cryptographic identity of that record and is
    suitable for anchoring on-chain.
    """

    receipt_id: str
    decision_id: str
    version: int
    state: str
    created_at: str
    payload: Dict[str, Any]
    receipt_commitment: str

    def to_dict(
        self,
        *,
        include_payload: bool = True,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "receipt_id": self.receipt_id,
            "decision_id": self.decision_id,
            "version": self.version,
            "state": self.state,
            "created_at": self.created_at,
            "receipt_commitment": self.receipt_commitment,
        }

        if include_payload:
            result["payload"] = self.payload

        return result


# ---------------------------------------------------------------------------
# Trust Receipt Builder
# ---------------------------------------------------------------------------

class TrustReceiptBuilder:
    """
    Build a canonical Enterprise Intelligence Trust Receipt.

    This builder intentionally produces a local structured receipt. It does
    not perform encryption or blockchain submission.

    Expected usage:

        builder = TrustReceiptBuilder(
            decision_id="EI-2026-001",
            payload={...}
        )

        receipt = builder.build()

        print(receipt.receipt_commitment)
    """

    def __init__(
        self,
        *,
        decision_id: str,
        payload: Mapping[str, Any],
        receipt_id: Optional[str] = None,
        version: int = 1,
        state: str = "active",
    ) -> None:

        if not decision_id.strip():
            raise TrustReceiptValidationError(
                "decision_id must not be empty"
            )

        if not isinstance(payload, Mapping):
            raise TrustReceiptValidationError(
                "payload must be a mapping"
            )

        if version <= 0:
            raise TrustReceiptValidationError(
                "version must be greater than zero"
            )

        if state not in {
            "active",
            "superseded",
            "cancelled",
        }:
            raise TrustReceiptValidationError(
                "unsupported Trust Receipt state"
            )

        self.decision_id = decision_id
        self.payload = dict(payload)

        self.receipt_id = (
            receipt_id
            if receipt_id is not None
            else f"TR-{decision_id}-V{version}"
        )

        self.version = version
        self.state = state

    # ------------------------------------------------------------------
    # Canonical payload
    # ------------------------------------------------------------------

    def build_payload(self) -> Dict[str, Any]:
        """
        Build the canonical protected receipt payload.

        The payload contains the decision context required to reconstruct
        how the enterprise decision was made.
        """

        payload = {
            "decision_id": self.decision_id,
            "receipt_id": self.receipt_id,
            "version": self.version,
            "state": self.state,
            "generated_at": utc_now(),
            "decision_record": self.payload,
        }

        return payload

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> TrustReceipt:
        """
        Build the Trust Receipt and calculate its commitment.
        """

        receipt_payload = self.build_payload()

        commitment = calculate_commitment(
            receipt_payload
        )

        return TrustReceipt(
            receipt_id=self.receipt_id,
            decision_id=self.decision_id,
            version=self.version,
            state=self.state,
            created_at=receipt_payload["generated_at"],
            payload=receipt_payload,
            receipt_commitment=commitment,
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    @staticmethod
    def verify(
        receipt: TrustReceipt,
    ) -> bool:
        """
        Recalculate and verify a Trust Receipt's commitment.
        """

        return verify_commitment(
            receipt.payload,
            receipt.receipt_commitment,
        )

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    @staticmethod
    def export_json(
        receipt: TrustReceipt,
        *,
        include_payload: bool = True,
    ) -> str:
        """
        Export the receipt as deterministic JSON.

        This representation can be encrypted by the application layer before
        protected storage.
        """

        return json.dumps(
            receipt.to_dict(
                include_payload=include_payload
            ),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )


# ---------------------------------------------------------------------------
# Receipt versioning
# ---------------------------------------------------------------------------

def create_superseding_receipt(
    previous_receipt: TrustReceipt,
    *,
    new_payload: Mapping[str, Any],
) -> TrustReceipt:
    """
    Create a new receipt version while preserving the previous receipt.

    The previous receipt is not modified.

    This implements the principle:

        "The enterprise can change its future without rewriting its past."
    """

    new_version = previous_receipt.version + 1

    builder = TrustReceiptBuilder(
        decision_id=previous_receipt.decision_id,
        receipt_id=(
            f"TR-{previous_receipt.decision_id}"
            f"-V{new_version}"
        ),
        version=new_version,
        state="active",
        payload={
            "previous_receipt_id": (
                previous_receipt.receipt_id
            ),
            "previous_receipt_commitment": (
                previous_receipt.receipt_commitment
            ),
            "new_decision_record": dict(new_payload),
        },
    )

    return builder.build()


# ---------------------------------------------------------------------------
# Commitment helpers
# ---------------------------------------------------------------------------

def build_evidence_commitment(
    evidence: Mapping[str, Any],
) -> str:
    """
    Generate a commitment for a normalized evidence object.
    """

    return calculate_commitment(evidence)


def build_decision_commitment(
    decision: Mapping[str, Any],
) -> str:
    """
    Generate a commitment for a normalized decision state.
    """

    return calculate_commitment(decision)


def build_trust_receipt_bundle(
    *,
    evidence: Mapping[str, Any],
    decision: Mapping[str, Any],
    receipt: TrustReceipt,
) -> Dict[str, str]:
    """
    Return the three primary commitments associated with the decision:

    - evidence commitment
    - decision commitment
    - full Trust Receipt commitment
    """

    return {
        "evidence_commitment": build_evidence_commitment(
            evidence
        ),
        "decision_commitment": build_decision_commitment(
            decision
        ),
        "receipt_commitment": receipt.receipt_commitment,
    }


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    decision_record = {
        "recommended_vendor": "Vendor A",
        "policy_id": "PROCUREMENT-POLICY-V1.2",
        "policy_result": "passed",
        "approval_status": "approved",
        "smart_account": (
            "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        ),
    }

    evidence_record = {
        "source_id": "SRC-001",
        "attestation_id": "DEMO-ATTESTATION-VND-001",
        "proof_reference": "DEMO-PROOF-VND-001",
        "verified": True,
        "regulatory_status": "active",
    }

    builder = TrustReceiptBuilder(
        decision_id="EI-2026-001",
        payload={
            "decision_record": decision_record,
            "evidence": evidence_record,
            "ai_findings": {
                "overall_risk": "low",
                "evidence_confidence": 0.92,
                "rank": 1,
            },
        },
    )

    receipt = builder.build()

    print("TRUST RECEIPT")
    print("=" * 60)
    print(
        TrustReceiptBuilder.export_json(
            receipt
        )
    )

    print("\nCOMMITMENT VERIFICATION")
    print("=" * 60)
    print(
        "valid:",
        TrustReceiptBuilder.verify(receipt),
    )

    print("\nCOMMITMENT")
    print("=" * 60)
    print(receipt.receipt_commitment)

    # Demonstrate versioning without altering the original.
    revised = create_superseding_receipt(
        receipt,
        new_payload={
            "reason": (
                "New verified external evidence triggered "
                "a board review."
            ),
            "new_status": "superseded",
        },
    )

    print("\nSUPERSEDING RECEIPT")
    print("=" * 60)
    print(
        f"{revised.receipt_id} "
        f"version={revised.version}"
    )
    print(
        f"previous={receipt.receipt_id}"
    )
