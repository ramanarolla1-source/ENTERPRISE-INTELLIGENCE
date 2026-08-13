"""
Enterprise Intelligence — Decision Engine

Purpose
-------
Evaluates vendor/counterparty intelligence against explicit enterprise policy.

Architectural boundary
----------------------
- Source intelligence qualifies external sources.
- FDC/Web2Json provides attested external evidence.
- AI interprets the verified evidence and produces structured assessments.
- THIS MODULE applies deterministic enterprise policy.
- Smart Account / on-chain contracts handle authorization and execution.

The decision engine does not:
- fetch external data;
- verify FDC proofs;
- call an LLM;
- authorize an executive decision;
- move funds;
- write to the blockchain.

It turns already-prepared evidence and AI assessments into a deterministic
policy result.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class DecisionStatus(str, Enum):
    ELIGIBLE = "eligible_for_approval"
    NOT_ELIGIBLE = "not_eligible_for_approval"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


# ---------------------------------------------------------------------------
# Policy model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EnterprisePolicy:
    """
    Deterministic policy applied to AI-produced assessments.

    minimum_evidence_confidence:
        Minimum confidence required before a candidate can be approved.

    maximum_permitted_risk:
        Highest acceptable overall risk.

    executive_approval_required:
        Whether a human/Smart Account approval is required after eligibility.
    """

    policy_id: str
    minimum_evidence_confidence: float = 0.80
    maximum_permitted_risk: RiskLevel = RiskLevel.MEDIUM
    executive_approval_required: bool = True

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("policy_id must not be empty")

        if not 0.0 <= self.minimum_evidence_confidence <= 1.0:
            raise ValueError(
                "minimum_evidence_confidence must be between 0.0 and 1.0"
            )


@dataclass(frozen=True)
class VendorAssessment:
    """
    Structured output expected from the AI decision-intelligence layer.

    This object represents an interpretation of already-verified evidence.
    """

    vendor_id: str
    vendor_name: str
    overall_risk: RiskLevel
    evidence_confidence: float
    rank: Optional[int] = None
    recommendation: Optional[str] = None
    findings: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.vendor_id.strip():
            raise ValueError("vendor_id must not be empty")

        if not self.vendor_name.strip():
            raise ValueError("vendor_name must not be empty")

        if not 0.0 <= self.evidence_confidence <= 1.0:
            raise ValueError(
                "evidence_confidence must be between 0.0 and 1.0"
            )


@dataclass(frozen=True)
class DecisionEvaluation:
    """
    Deterministic result produced by the decision engine.
    """

    vendor_id: str
    vendor_name: str
    status: DecisionStatus
    risk_level: RiskLevel
    evidence_confidence: float
    policy_id: str
    reasons: List[str]
    eligible_for_executive_approval: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Risk ordering
# ---------------------------------------------------------------------------

_RISK_ORDER = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.UNKNOWN: 99,
}


def risk_exceeds(
    actual: RiskLevel,
    maximum_permitted: RiskLevel,
) -> bool:
    """
    Return True when the actual risk exceeds enterprise policy.

    UNKNOWN is treated as exceeding the policy because an enterprise should
    not silently treat an unknown risk level as acceptable.
    """

    if actual == RiskLevel.UNKNOWN:
        return True

    return _RISK_ORDER[actual] > _RISK_ORDER[maximum_permitted]


# ---------------------------------------------------------------------------
# Decision Engine
# ---------------------------------------------------------------------------

class DecisionEngine:
    """
    Deterministic enterprise policy engine.

    The engine evaluates one or more AI-produced VendorAssessment objects
    against an explicit EnterprisePolicy.

    This design intentionally keeps the AI layer and authorization layer
    separate from deterministic policy enforcement.
    """

    def __init__(self, policy: EnterprisePolicy) -> None:
        if not isinstance(policy, EnterprisePolicy):
            raise TypeError("policy must be an EnterprisePolicy")

        self.policy = policy

    # ---------------------------------------------------------------------
    # Single candidate evaluation
    # ---------------------------------------------------------------------

    def evaluate(
        self,
        assessment: VendorAssessment,
    ) -> DecisionEvaluation:
        """
        Evaluate one vendor assessment against enterprise policy.
        """

        reasons: List[str] = []

        # -------------------------------------------------------------
        # Evidence confidence
        # -------------------------------------------------------------

        if (
            assessment.evidence_confidence
            < self.policy.minimum_evidence_confidence
        ):
            reasons.append(
                "Evidence confidence is below the enterprise minimum."
            )

        # -------------------------------------------------------------
        # Risk threshold
        # -------------------------------------------------------------

        if risk_exceeds(
            assessment.overall_risk,
            self.policy.maximum_permitted_risk,
        ):
            reasons.append(
                "Overall risk exceeds the maximum risk permitted by policy."
            )

        # -------------------------------------------------------------
        # Final decision
        # -------------------------------------------------------------

        if (
            assessment.overall_risk == RiskLevel.UNKNOWN
            or assessment.evidence_confidence
            < self.policy.minimum_evidence_confidence
        ):
            status = DecisionStatus.INSUFFICIENT_EVIDENCE

        elif reasons:
            status = DecisionStatus.NOT_ELIGIBLE

        else:
            status = DecisionStatus.ELIGIBLE

        eligible_for_approval = status == DecisionStatus.ELIGIBLE

        if eligible_for_approval:
            reasons.append("Assessment satisfies enterprise policy.")

            if self.policy.executive_approval_required:
                reasons.append(
                    "Executive authorization is required before execution."
                )

        return DecisionEvaluation(
            vendor_id=assessment.vendor_id,
            vendor_name=assessment.vendor_name,
            status=status,
            risk_level=assessment.overall_risk,
            evidence_confidence=assessment.evidence_confidence,
            policy_id=self.policy.policy_id,
            reasons=reasons,
            eligible_for_executive_approval=eligible_for_approval,
        )

    # ---------------------------------------------------------------------
    # Candidate ranking
    # ---------------------------------------------------------------------

    def rank_candidates(
        self,
        assessments: Iterable[VendorAssessment],
    ) -> List[DecisionEvaluation]:
        """
        Evaluate and rank candidate vendors.

        Ranking principle:
        1. Policy eligibility
        2. Lower risk
        3. Higher evidence confidence
        4. Existing AI rank, when supplied

        Enterprise private inputs such as quoted price or technical suitability
        can be incorporated by a higher-level application layer. This module
        deliberately focuses on the policy decision derived from the
        intelligence layer.
        """

        evaluations = [
            self.evaluate(assessment)
            for assessment in assessments
        ]

        def sort_key(result: DecisionEvaluation) -> tuple:
            eligible = 0 if result.eligible_for_executive_approval else 1
            risk = _RISK_ORDER[result.risk_level]
            confidence = -result.evidence_confidence

            return (
                eligible,
                risk,
                confidence,
                result.vendor_name.lower(),
            )

        return sorted(evaluations, key=sort_key)

    # ---------------------------------------------------------------------
    # Recommended candidate
    # ---------------------------------------------------------------------

    def recommend(
        self,
        assessments: Iterable[VendorAssessment],
    ) -> Optional[DecisionEvaluation]:
        """
        Return the strongest policy-eligible candidate.

        Returns None when no candidate satisfies policy.
        """

        ranked = self.rank_candidates(assessments)

        for result in ranked:
            if result.eligible_for_executive_approval:
                return result

        return None

    # ---------------------------------------------------------------------
    # Decision summary
    # ---------------------------------------------------------------------

    def build_decision_summary(
        self,
        assessments: Iterable[VendorAssessment],
    ) -> Dict[str, Any]:
        """
        Build a serializable summary suitable for a Trust Receipt input.
        """

        ranked = self.rank_candidates(assessments)
        recommended = next(
            (
                item for item in ranked
                if item.eligible_for_executive_approval
            ),
            None,
        )

        return {
            "policy": {
                "policy_id": self.policy.policy_id,
                "minimum_evidence_confidence": (
                    self.policy.minimum_evidence_confidence
                ),
                "maximum_permitted_risk": (
                    self.policy.maximum_permitted_risk.value
                ),
                "executive_approval_required": (
                    self.policy.executive_approval_required
                ),
            },
            "candidates": [
                item.to_dict()
                for item in ranked
            ],
            "recommended_vendor": (
                {
                    "vendor_id": recommended.vendor_id,
                    "vendor_name": recommended.vendor_name,
                }
                if recommended
                else None
            ),
            "decision_ready_for_authorization": recommended is not None,
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def evaluate_vendor_selection(
    assessments: Iterable[VendorAssessment],
    policy: EnterprisePolicy,
) -> Dict[str, Any]:
    """
    Convenience wrapper for the common vendor-selection workflow.
    """

    engine = DecisionEngine(policy)
    return engine.build_decision_summary(assessments)


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    policy = EnterprisePolicy(
        policy_id="PROCUREMENT-POLICY-V1.2",
        minimum_evidence_confidence=0.80,
        maximum_permitted_risk=RiskLevel.MEDIUM,
        executive_approval_required=True,
    )

    assessments = [
        VendorAssessment(
            vendor_id="VND-001",
            vendor_name="Vendor A",
            overall_risk=RiskLevel.LOW,
            evidence_confidence=0.94,
            rank=1,
            recommendation="preferred",
            findings={
                "regulatory": "low",
                "corporate": "low",
                "operational": "low",
            },
        ),
        VendorAssessment(
            vendor_id="VND-002",
            vendor_name="Vendor B",
            overall_risk=RiskLevel.MEDIUM,
            evidence_confidence=0.89,
            rank=2,
            recommendation="acceptable_alternative",
            findings={
                "regulatory": "medium",
                "corporate": "low",
                "operational": "medium",
            },
        ),
        VendorAssessment(
            vendor_id="VND-003",
            vendor_name="Vendor C",
            overall_risk=RiskLevel.HIGH,
            evidence_confidence=0.81,
            rank=3,
            recommendation="not_preferred",
            findings={
                "regulatory": "high",
                "corporate": "medium",
                "operational": "medium",
            },
        ),
    ]

    result = evaluate_vendor_selection(
        assessments=assessments,
        policy=policy,
    )

    import json

    print(json.dumps(result, indent=2))
