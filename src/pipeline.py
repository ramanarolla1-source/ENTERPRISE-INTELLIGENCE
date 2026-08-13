"""
Enterprise Intelligence — End-to-End Decision Pipeline

Purpose
-------
Orchestrates the demonstration workflow:

    Source Registry
        ↓
    AI Source Intelligence
        ↓
    FDC / Web2Json Evidence Pipeline
        ↓
    Verified Evidence
        ↓
    AI Decision Intelligence
        ↓
    Deterministic Enterprise Policy
        ↓
    Trust Receipt Preparation
        ↓
    Smart Account / On-chain Execution boundary

Architectural boundaries
------------------------
This module coordinates the application. It does not:

- claim that arbitrary Web2 sources are truthful;
- implement the FDC protocol itself;
- give AI executive authority;
- sign Smart Account transactions;
- move funds;
- replace the enterprise policy engine.

The pipeline prepares a decision for authorization and execution.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

try:
    from .decision_engine import (
        DecisionEngine,
        EnterprisePolicy,
        RiskLevel,
        VendorAssessment,
    )
    from .evidence_pipeline import (
        EvidencePipeline,
        EvidenceRecord,
        SourceMetadata,
    )
    from .trust_receipt import TrustReceiptBuilder
except ImportError:
    # Allows direct execution:
    # python src/pipeline.py
    from decision_engine import (
        DecisionEngine,
        EnterprisePolicy,
        RiskLevel,
        VendorAssessment,
    )
    from evidence_pipeline import (
        EvidencePipeline,
        EvidenceRecord,
        SourceMetadata,
    )
    from trust_receipt import TrustReceiptBuilder


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------

@dataclass
class CandidateResult:
    vendor_id: str
    vendor_name: str
    evidence: List[EvidenceRecord]
    assessment: VendorAssessment


@dataclass
class PipelineResult:
    decision_id: str
    policy_id: str
    status: str
    candidates: List[CandidateResult]
    recommended_vendor: Optional[str]
    recommended_vendor_id: Optional[str]
    decision_summary: Dict[str, Any]
    trust_receipt: Dict[str, Any]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _risk_level(value: str) -> RiskLevel:
    try:
        return RiskLevel(value.lower())
    except ValueError as exc:
        raise ValueError(
            f"Unsupported risk level: {value!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Source registry adapter
# ---------------------------------------------------------------------------

class SourceRegistry:
    """
    Loads the demonstration source catalogue.

    In a production implementation this may be backed by:
    - enterprise source governance;
    - a database;
    - a managed source registry;
    - or another policy-controlled configuration system.
    """

    def __init__(self, sources: Mapping[str, Any]) -> None:
        self._sources = {
            source["source_id"]: source
            for source in sources.get("sources", [])
        }

    def get(self, source_id: str) -> Dict[str, Any]:
        try:
            return self._sources[source_id]
        except KeyError as exc:
            raise KeyError(
                f"Source not found in registry: {source_id}"
            ) from exc

    def build_source_metadata(self, source_id: str) -> SourceMetadata:
        source = self.get(source_id)

        ai = source.get("ai_assessment", {})

        return SourceMetadata(
            source_id=source["source_id"],
            name=source["name"],
            publisher=source["publisher"],
            source_type=source["source_type"],
            url=source["url"],
            source_classification=ai.get(
                "classification",
                "context_only",
            ),
            supports_web2json=bool(
                source.get("supports_web2json", False)
            ),
            authority_score=float(ai.get("authority", 0.0)),
            provenance_score=float(ai.get("provenance", 0.0)),
            relevance_score=float(ai.get("relevance", 0.0)),
            freshness_score=float(ai.get("freshness", 0.0)),
            corroboration_score=float(ai.get("corroboration", 0.0)),
        )


# ---------------------------------------------------------------------------
# AI Source Intelligence
# ---------------------------------------------------------------------------

class SourceIntelligence:
    """
    Demonstration source-selection layer.

    The data in sources.json already contains the source assessments used by
    the demo. This class turns those assessments into a deterministic
    preferred-source selection.

    A live deployment can replace this class with an LLM-assisted workflow,
    while retaining the same output contract.
    """

    _CLASS_PRIORITY = {
        "preferred": 0,
        "secondary": 1,
        "context_only": 2,
        "reject": 3,
    }

    def __init__(self, registry: SourceRegistry) -> None:
        self.registry = registry

    def rank_source_ids(
        self,
        source_ids: Sequence[str],
    ) -> List[str]:
        """
        Rank candidate source IDs by classification and source confidence.
        """

        ranked = []

        for source_id in source_ids:
            source = self.registry.get(source_id)
            ai = source.get("ai_assessment", {})

            classification = str(
                ai.get("classification", "context_only")
            ).lower()

            overall = float(ai.get("overall", 0.0))

            ranked.append(
                (
                    self._CLASS_PRIORITY.get(
                        classification,
                        99,
                    ),
                    -overall,
                    source_id,
                )
            )

        ranked.sort()

        return [item[2] for item in ranked]

    def select_preferred_source(
        self,
        source_ids: Sequence[str],
    ) -> SourceMetadata:
        """
        Select the highest-ranked source that is suitable for Web2Json.
        """

        for source_id in self.rank_source_ids(source_ids):
            source = self.registry.get(source_id)

            classification = str(
                source.get("ai_assessment", {})
                .get("classification", "context_only")
            ).lower()

            if (
                classification in {"preferred", "secondary"}
                and source.get("supports_web2json") is True
            ):
                return self.registry.build_source_metadata(source_id)

        raise ValueError(
            "No supported preferred/secondary Web2Json source "
            "was found for the candidate"
        )


# ---------------------------------------------------------------------------
# Decision Pipeline
# ---------------------------------------------------------------------------

class EnterpriseDecisionPipeline:
    """
    End-to-end Enterprise Intelligence orchestration layer.
    """

    def __init__(
        self,
        *,
        sources: Mapping[str, Any],
        vendors: Mapping[str, Any],
        decision: Mapping[str, Any],
    ) -> None:
        self.sources = sources
        self.vendors = vendors
        self.decision = decision

        self.registry = SourceRegistry(sources)
        self.source_intelligence = SourceIntelligence(self.registry)

        self.evidence_pipeline = EvidencePipeline()

        policy_data = decision.get("enterprise_policy", {})

        self.policy = EnterprisePolicy(
            policy_id=policy_data.get(
                "policy_id",
                "UNSPECIFIED-POLICY",
            ),
            minimum_evidence_confidence=float(
                policy_data.get(
                    "minimum_evidence_confidence",
                    0.80,
                )
            ),
            maximum_permitted_risk=_risk_level(
                policy_data.get(
                    "maximum_permitted_risk",
                    "medium",
                )
            ),
            executive_approval_required=bool(
                policy_data.get(
                    "executive_approval_required",
                    True,
                )
            ),
        )

        self.decision_engine = DecisionEngine(self.policy)

    # ------------------------------------------------------------------
    # Source / evidence processing
    # ------------------------------------------------------------------

    def _build_vendor_evidence(
        self,
        vendor: Mapping[str, Any],
    ) -> List[EvidenceRecord]:
        """
        Build evidence records for the vendor.

        The demonstration dataset contains normalized public evidence. In a
        live implementation, `response` would come from an actual FDC/Web2Json
        attested response after successful proof verification.
        """

        vendor_id = vendor["vendor_id"]

        public_evidence = vendor.get(
            "public_evidence",
            {},
        )

        source_ids = list(
            public_evidence.get(
                "source_ids",
                [],
            )
        )

        if not source_ids:
            raise ValueError(
                f"No source IDs configured for {vendor_id}"
            )

        selected_source = (
            self.source_intelligence.select_preferred_source(
                source_ids
            )
        )

        # --------------------------------------------------------------
        # Demonstration response
        # --------------------------------------------------------------
        #
        # This is intentionally synthetic. A production implementation
        # would replace this object with the actual response produced by
        # the live Web2Json/FDC workflow.
        #
        response = {
            "regulatory_status": public_evidence.get(
                "regulatory_status"
            ),
            "registration_status": public_evidence.get(
                "registration_status"
            ),
            "recent_update": public_evidence.get(
                "recent_update"
            ),
            "external_risk_signal": public_evidence.get(
                "external_risk_signal"
            ),
            "evidence_confidence": public_evidence.get(
                "evidence_confidence"
            ),
        }

        required_fields = [
            "regulatory_status",
            "registration_status",
            "recent_update",
            "external_risk_signal",
        ]

        evidence_id = (
            f"EVD-{self.decision['decision_id']}-{vendor_id}"
        )

        evidence = self.evidence_pipeline.build_evidence(
            decision_id=self.decision["decision_id"],
            evidence_id=evidence_id,
            source=selected_source,
            response=response,
            required_fields=required_fields,
            verification_mode="demonstration",
            attestation_id=f"DEMO-ATTESTATION-{vendor_id}",
            proof_reference=f"DEMO-PROOF-{vendor_id}",
        )

        return [evidence]

    # ------------------------------------------------------------------
    # AI Decision Intelligence
    # ------------------------------------------------------------------

    @staticmethod
    def _build_vendor_assessment(
        vendor: Mapping[str, Any],
        evidence: Sequence[EvidenceRecord],
    ) -> VendorAssessment:
        """
        Build the structured assessment consumed by DecisionEngine.

        The demo data already contains the AI assessment in vendors.json.

        A live application would replace this method with the actual AI
        reasoning / structured-output layer.
        """

        ai = vendor.get(
            "ai_assessment",
            {},
        )

        if not evidence:
            raise ValueError(
                f"No evidence available for {vendor['vendor_id']}"
            )

        # Use the minimum evidence confidence across the evidence set.
        #
        # This is intentionally conservative: one weak evidence item should
        # not be hidden by several stronger items.
        evidence_confidence = min(
            item.evidence_confidence
            for item in evidence
        )

        # Demonstration AI assessment may provide a lower/higher confidence
        # value. We never increase it beyond the verified evidence ceiling.
        configured_confidence = float(
            ai.get(
                "confidence",
                evidence_confidence,
            )
        )

        final_confidence = min(
            configured_confidence,
            evidence_confidence,
        )

        return VendorAssessment(
            vendor_id=vendor["vendor_id"],
            vendor_name=vendor["name"],
            overall_risk=_risk_level(
                ai.get(
                    "overall_risk",
                    "unknown",
                )
            ),
            evidence_confidence=round(
                final_confidence,
                4,
            ),
            rank=ai.get("rank"),
            recommendation=ai.get("recommendation"),
            findings={
                "corporate_risk": ai.get(
                    "corporate_risk"
                ),
                "regulatory_risk": ai.get(
                    "regulatory_risk"
                ),
                "operational_risk": ai.get(
                    "operational_risk"
                ),
                "reputational_risk": ai.get(
                    "reputational_risk"
                ),
            },
        )

    # ------------------------------------------------------------------
    # Trust Receipt
    # ------------------------------------------------------------------

    def _build_trust_receipt(
        self,
        *,
        candidates: Sequence[CandidateResult],
        decision_summary: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the Trust Receipt payload.

        The exact TrustReceiptBuilder API is intentionally isolated here so
        the rest of the pipeline does not depend on storage details.
        """

        receipt_data = {
            "decision_id": self.decision["decision_id"],
            "decision_type": self.decision.get(
                "decision_type",
                "enterprise_decision",
            ),
            "title": self.decision.get(
                "title",
                "Enterprise Decision",
            ),
            "policy": decision_summary.get(
                "policy",
                {},
            ),
            "candidate_results": [
                {
                    "vendor_id": item.vendor_id,
                    "vendor_name": item.vendor_name,
                    "assessment": asdict(
                        item.assessment
                    ),
                    "evidence": [
                        {
                            "evidence_id": ev.evidence_id,
                            "source_id": ev.source.source_id,
                            "source_name": ev.source.name,
                            "attestation_id": (
                                ev.verification.attestation_id
                            ),
                            "proof_reference": (
                                ev.verification.proof_reference
                            ),
                            "verification_mode": (
                                ev.verification.verification_mode
                            ),
                            "evidence_commitment": (
                                ev.evidence_commitment
                            ),
                        }
                        for ev in item.evidence
                    ],
                }
                for item in candidates
            ],
            "recommendation": decision_summary.get(
                "recommended_vendor"
            ),
            "generated_at": _utc_now(),
        }

        # If trust_receipt.py exposes a builder implementation, use it.
        #
        # The fallback keeps the pipeline runnable even when the receipt
        # builder is still under development.
        try:
            builder = TrustReceiptBuilder(
                decision_id=self.decision["decision_id"],
                payload=receipt_data,
            )

            receipt = builder.build()

            if hasattr(receipt, "to_dict"):
                return receipt.to_dict()

            if isinstance(receipt, Mapping):
                return dict(receipt)

        except TypeError:
            # Allows for a different builder constructor during iterative
            # hackathon development.
            pass
        except AttributeError:
            pass

        return receipt_data

    # ------------------------------------------------------------------
    # Execute complete pipeline
    # ------------------------------------------------------------------

    def run(self) -> PipelineResult:
        """
        Execute the demonstration workflow.

        Returns:
            PipelineResult containing candidate evidence, deterministic
            policy evaluation, recommendation and Trust Receipt data.
        """

        vendor_records = self.vendors.get(
            "vendors",
            [],
        )

        if not vendor_records:
            raise ValueError(
                "Vendor dataset does not contain any vendors"
            )

        candidates: List[CandidateResult] = []

        assessments: List[VendorAssessment] = []
        evidence_by_vendor: Dict[str, List[EvidenceRecord]] = {}

        # --------------------------------------------------------------
        # Process each candidate
        # --------------------------------------------------------------

        for vendor in vendor_records:
            evidence = self._build_vendor_evidence(vendor)

            assessment = self._build_vendor_assessment(
                vendor,
                evidence,
            )

            evidence_by_vendor[vendor["vendor_id"]] = evidence
            assessments.append(assessment)

        # --------------------------------------------------------------
        # Apply deterministic enterprise policy
        # --------------------------------------------------------------

        decision_summary = self.decision_engine.build_decision_summary(
            assessments
        )

        for assessment in assessments:
            evaluation = self.decision_engine.evaluate(
                assessment
            )

            candidates.append(
                CandidateResult(
                    vendor_id=assessment.vendor_id,
                    vendor_name=assessment.vendor_name,
                    evidence=evidence_by_vendor[
                        assessment.vendor_id
                    ],
                    assessment=assessment,
                )
            )

        recommended = self.decision_engine.recommend(
            assessments
        )

        recommended_vendor = (
            recommended.vendor_name
            if recommended
            else None
        )

        recommended_vendor_id = (
            recommended.vendor_id
            if recommended
            else None
        )

        # --------------------------------------------------------------
        # Prepare Trust Receipt
        # --------------------------------------------------------------

        trust_receipt = self._build_trust_receipt(
            candidates=candidates,
            decision_summary=decision_summary,
        )

        status = (
            "ready_for_executive_approval"
            if recommended
            else "no_candidate_meets_policy"
        )

        return PipelineResult(
            decision_id=self.decision["decision_id"],
            policy_id=self.policy.policy_id,
            status=status,
            candidates=candidates,
            recommended_vendor=recommended_vendor,
            recommended_vendor_id=recommended_vendor_id,
            decision_summary=decision_summary,
            trust_receipt=trust_receipt,
            generated_at=_utc_now(),
        )


# ---------------------------------------------------------------------------
# File-based demo runner
# ---------------------------------------------------------------------------

def run_demo_from_repository(
    repository_root: Optional[Path] = None,
) -> PipelineResult:
    """
    Run the demonstration using the repository's sample data.
    """

    root = repository_root or Path(__file__).resolve().parents[1]

    sources_path = root / "data" / "sources.json"
    vendors_path = root / "data" / "vendors.json"
    decision_path = root / "data" / "sample_decision.json"

    sources = _load_json(sources_path)
    vendors = _load_json(vendors_path)
    decision = _load_json(decision_path)

    pipeline = EnterpriseDecisionPipeline(
        sources=sources,
        vendors=vendors,
        decision=decision,
    )

    return pipeline.run()


# ---------------------------------------------------------------------------
# CLI demonstration
# ---------------------------------------------------------------------------

def main() -> None:
    result = run_demo_from_repository()

    print(
        json.dumps(
            {
                "decision_id": result.decision_id,
                "policy_id": result.policy_id,
                "status": result.status,
                "recommended_vendor": (
                    result.recommended_vendor
                ),
                "recommended_vendor_id": (
                    result.recommended_vendor_id
                ),
                "generated_at": result.generated_at,
            },
            indent=2,
        )
    )

    print("\nCandidate Results:")

    for candidate in result.candidates:
        print(
            f"- {candidate.vendor_name}: "
            f"{candidate.assessment.overall_risk.value.upper()} "
            f"(confidence="
            f"{candidate.assessment.evidence_confidence:.2f})"
        )

    print("\nTrust Receipt prepared.")
    print(
        "Smart Account authorization and on-chain execution "
        "remain explicit next-step boundaries."
    )


if __name__ == "__main__":
    main()
