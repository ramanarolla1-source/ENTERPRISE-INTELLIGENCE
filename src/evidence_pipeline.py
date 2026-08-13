"""
Enterprise Intelligence — Evidence Pipeline

Purpose
-------
Transforms a selected public Web2 source response into a structured,
traceable evidence object suitable for AI interpretation and later inclusion
in a Trust Receipt.

Architectural boundary
----------------------
AI Source Intelligence:
    Determines which source is suitable.

FDC / Web2Json:
    Provides an attested representation of the selected supported Web2
    response.

Evidence Pipeline (this module):
    Validates the expected structure, extracts relevant fields, creates a
    canonical evidence object, and generates an evidence commitment.

AI Decision Intelligence:
    Interprets the verified evidence.

Enterprise Policy:
    Applies deterministic business rules.

IMPORTANT
---------
This prototype does not pretend to be the Flare FDC verifier itself.

The `FDCAdapter` abstraction represents the boundary where a live deployment
would submit/retrieve/verify the relevant Web2Json attestation. Demonstration
data can be passed through the same pipeline so the architecture remains
reproducible without fabricating a live FDC proof.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class EvidencePipelineError(Exception):
    """Base exception for evidence pipeline errors."""


class SourceValidationError(EvidencePipelineError):
    """Raised when source metadata does not satisfy expected requirements."""


class EvidenceValidationError(EvidencePipelineError):
    """Raised when the attested response is invalid or incomplete."""


class FDCVerificationError(EvidencePipelineError):
    """Raised when the FDC adapter reports an invalid attestation."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SourceMetadata:
    """
    Metadata describing the selected external source.

    This does not claim that the source is inherently truthful. It records
    why the application considers the source suitable for the evidence path.
    """

    source_id: str
    name: str
    publisher: str
    source_type: str
    url: str
    source_classification: str
    supports_web2json: bool

    authority_score: float
    provenance_score: float
    relevance_score: float
    freshness_score: float
    corroboration_score: float

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")

        if not self.name.strip():
            raise ValueError("source name must not be empty")

        if not self.publisher.strip():
            raise ValueError("publisher must not be empty")

        if not self.url.strip():
            raise ValueError("url must not be empty")

        if not self.supports_web2json:
            raise SourceValidationError(
                "Selected source is not marked as Web2Json-compatible"
            )

        for field_name, value in (
            ("authority_score", self.authority_score),
            ("provenance_score", self.provenance_score),
            ("relevance_score", self.relevance_score),
            ("freshness_score", self.freshness_score),
            ("corroboration_score", self.corroboration_score),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be between 0.0 and 1.0"
                )


@dataclass(frozen=True)
class FDCVerificationResult:
    """
    Result of the FDC/Web2Json verification boundary.

    In a live implementation:
        - attestation_id should identify the actual FDC attestation;
        - proof_reference should identify the proof;
        - verified should represent actual proof verification.

    In a demonstration:
        - placeholder identifiers may be used, but the status must be marked
          as demonstration rather than misrepresented as live verification.
    """

    verified: bool
    attestation_id: str
    proof_reference: str
    verification_mode: str  # e.g. "live" or "demonstration"
    request_commitment: Optional[str] = None
    raw_response_hash: Optional[str] = None

    def __post_init__(self) -> None:
        if self.verification_mode not in {"live", "demonstration"}:
            raise ValueError(
                "verification_mode must be 'live' or 'demonstration'"
            )

        if self.verified and not self.attestation_id.strip():
            raise ValueError(
                "Verified evidence requires an attestation_id"
            )

        if self.verified and not self.proof_reference.strip():
            raise ValueError(
                "Verified evidence requires a proof_reference"
            )


@dataclass(frozen=True)
class EvidenceRecord:
    """
    Canonical evidence record consumed by the intelligence layer.

    This record intentionally stores the extracted evidence rather than
    unnecessarily retaining the complete Web2 response.
    """

    evidence_id: str
    decision_id: str
    source: SourceMetadata
    verification: FDCVerificationResult

    extracted_data: Mapping[str, Any]

    source_confidence: float
    evidence_confidence: float

    retrieved_at: str
    normalized_at: str

    evidence_commitment: str

    provenance_note: str = field(
        default=(
            "Evidence represents an attested response from the selected "
            "supported source; it is not an assertion that the source is "
            "universally truthful."
        )
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def _canonical_json(value: Any) -> str:
    """
    Produce stable JSON for hashing and commitments.
    """

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def sha256_commitment(value: Any) -> str:
    """
    Generate a deterministic SHA-256 commitment.

    The resulting value is prefixed with 0x so it can be represented in a
    blockchain-oriented context.
    """

    canonical = _canonical_json(value).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()

    return f"0x{digest}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def calculate_source_confidence(source: SourceMetadata) -> float:
    """
    Calculate a simple deterministic source-confidence score from the
    AI-produced source assessment.

    This is intentionally transparent rather than pretending to be a
    cryptographic trust score.

    Equal weighting keeps the demonstration easy to understand.
    """

    values = [
        source.authority_score,
        source.provenance_score,
        source.relevance_score,
        source.freshness_score,
        source.corroboration_score,
    ]

    return round(sum(values) / len(values), 4)


def calculate_evidence_confidence(
    source_confidence: float,
    verification: FDCVerificationResult,
) -> float:
    """
    Calculate evidence confidence.

    Verification status is a gating condition, not an arbitrary boost.

    If the FDC verification is invalid, the evidence cannot be treated as
    decision-grade evidence.
    """

    if not verification.verified:
        return 0.0

    # The prototype keeps the evidence confidence tied to the qualified
    # source score. In a production system this can incorporate additional
    # corroboration, freshness and domain-specific evidence controls.
    return round(source_confidence, 4)


# ---------------------------------------------------------------------------
# FDC adapter
# ---------------------------------------------------------------------------

class FDCAdapter:
    """
    Boundary between the application and the real Flare FDC/Web2Json stack.

    This class deliberately does not invent a live FDC verifier implementation.

    A production adapter should:
        1. construct the correct Web2Json attestation request;
        2. submit the request to the configured Flare environment;
        3. retrieve the attested response / proof;
        4. validate the relevant FDC verification result;
        5. return FDCVerificationResult.
    """

    def verify_web2json(
        self,
        *,
        source: SourceMetadata,
        response: Mapping[str, Any],
        mode: str = "demonstration",
        attestation_id: str = "DEMO-ATTESTATION",
        proof_reference: str = "DEMO-PROOF",
    ) -> FDCVerificationResult:
        """
        Demonstration-friendly verification boundary.

        In `live` mode this method should be replaced/extended with actual
        FDC request submission and proof verification.
        """

        if mode not in {"live", "demonstration"}:
            raise ValueError(
                "mode must be 'live' or 'demonstration'"
            )

        if not source.supports_web2json:
            raise FDCVerificationError(
                "Source is not configured for Web2Json"
            )

        if not response:
            raise EvidenceValidationError(
                "Web2 response is empty"
            )

        raw_response_hash = sha256_commitment(response)

        if mode == "demonstration":
            return FDCVerificationResult(
                verified=True,
                attestation_id=attestation_id,
                proof_reference=proof_reference,
                verification_mode="demonstration",
                raw_response_hash=raw_response_hash,
            )

        # Do not claim live verification without a real adapter.
        raise NotImplementedError(
            "Live FDC/Web2Json integration must be implemented using "
            "the current Flare network configuration and verifier."
        )


# ---------------------------------------------------------------------------
# Evidence Pipeline
# ---------------------------------------------------------------------------

class EvidencePipeline:
    """
    Converts a selected supported Web2 response into a canonical EvidenceRecord.
    """

    def __init__(self, fdc_adapter: Optional[FDCAdapter] = None) -> None:
        self.fdc_adapter = fdc_adapter or FDCAdapter()

    def validate_source(
        self,
        source: SourceMetadata,
    ) -> None:
        """
        Ensure the source is eligible for the evidence pipeline.
        """

        if source.source_classification.lower() not in {
            "preferred",
            "secondary",
        }:
            raise SourceValidationError(
                "Only preferred or secondary sources may enter "
                "the evidence verification pipeline"
            )

        if not source.supports_web2json:
            raise SourceValidationError(
                "Selected source does not support Web2Json"
            )

    def validate_response(
        self,
        response: Mapping[str, Any],
        required_fields: Optional[list[str]] = None,
    ) -> None:
        """
        Validate the structure of an external response.

        `required_fields` refers to top-level JSON keys in this prototype.
        """

        if not isinstance(response, Mapping):
            raise EvidenceValidationError(
                "Web2 response must be a mapping/object"
            )

        if not response:
            raise EvidenceValidationError(
                "Web2 response must not be empty"
            )

        if required_fields:
            missing = [
                field
                for field in required_fields
                if field not in response
            ]

            if missing:
                raise EvidenceValidationError(
                    "Required fields missing from response: "
                    + ", ".join(missing)
                )

    def build_evidence(
        self,
        *,
        decision_id: str,
        evidence_id: str,
        source: SourceMetadata,
        response: Mapping[str, Any],
        required_fields: Optional[list[str]] = None,
        verification_mode: str = "demonstration",
        attestation_id: str = "DEMO-ATTESTATION",
        proof_reference: str = "DEMO-PROOF",
    ) -> EvidenceRecord:
        """
        Complete evidence-processing flow.

        1. Validate source
        2. Validate response
        3. Request/verify FDC boundary
        4. Calculate source/evidence confidence
        5. Normalize extracted data
        6. Generate evidence commitment
        """

        if not decision_id.strip():
            raise ValueError("decision_id must not be empty")

        if not evidence_id.strip():
            raise ValueError("evidence_id must not be empty")

        self.validate_source(source)

        self.validate_response(
            response,
            required_fields=required_fields,
        )

        retrieved_at = utc_now()

        verification = self.fdc_adapter.verify_web2json(
            source=source,
            response=response,
            mode=verification_mode,
            attestation_id=attestation_id,
            proof_reference=proof_reference,
        )

        if not verification.verified:
            raise FDCVerificationError(
                "FDC verification did not succeed"
            )

        source_confidence = calculate_source_confidence(source)

        evidence_confidence = calculate_evidence_confidence(
            source_confidence=source_confidence,
            verification=verification,
        )

        # Keep only relevant extracted data instead of automatically
        # retaining the complete external response.
        extracted_data: Dict[str, Any]

        if required_fields:
            extracted_data = {
                field: response[field]
                for field in required_fields
            }
        else:
            extracted_data = dict(response)

        normalized_at = utc_now()

        commitment_payload = {
            "evidence_id": evidence_id,
            "decision_id": decision_id,
            "source": {
                "source_id": source.source_id,
                "url": source.url,
            },
            "verification": {
                "attestation_id": verification.attestation_id,
                "proof_reference": verification.proof_reference,
                "verification_mode": verification.verification_mode,
                "request_commitment": verification.request_commitment,
            },
            "extracted_data": extracted_data,
            "source_confidence": source_confidence,
            "evidence_confidence": evidence_confidence,
            "retrieved_at": retrieved_at,
        }

        evidence_commitment = sha256_commitment(
            commitment_payload
        )

        return EvidenceRecord(
            evidence_id=evidence_id,
            decision_id=decision_id,
            source=source,
            verification=verification,
            extracted_data=extracted_data,
            source_confidence=source_confidence,
            evidence_confidence=evidence_confidence,
            retrieved_at=retrieved_at,
            normalized_at=normalized_at,
            evidence_commitment=evidence_commitment,
        )


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def process_web2_evidence(
    *,
    decision_id: str,
    evidence_id: str,
    source: SourceMetadata,
    response: Mapping[str, Any],
    required_fields: Optional[list[str]] = None,
) -> EvidenceRecord:
    """
    Convenience wrapper for the demonstration workflow.
    """

    pipeline = EvidencePipeline()

    return pipeline.build_evidence(
        decision_id=decision_id,
        evidence_id=evidence_id,
        source=source,
        response=response,
        required_fields=required_fields,
        verification_mode="demonstration",
    )


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    source = SourceMetadata(
        source_id="SRC-001",
        name="Official Regulatory API",
        publisher="Relevant Regulatory Authority",
        source_type="regulatory",
        url="https://example-regulator.gov/api/entities",
        source_classification="preferred",
        supports_web2json=True,
        authority_score=0.99,
        provenance_score=0.99,
        relevance_score=0.96,
        freshness_score=0.95,
        corroboration_score=0.94,
    )

    response = {
        "registration_status": "active",
        "license_status": "valid",
        "last_updated": "2026-08-13",
    }

    evidence = process_web2_evidence(
        decision_id="EI-2026-001",
        evidence_id="EVD-001",
        source=source,
        response=response,
        required_fields=[
            "registration_status",
            "license_status",
            "last_updated",
        ],
    )

    print(
        json.dumps(
            evidence.to_dict(),
            indent=2,
            default=str,
        )
    )
