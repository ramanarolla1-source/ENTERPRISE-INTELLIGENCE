"""
Enterprise Intelligence — AI Source Intelligence

Purpose
-------
Evaluate and rank candidate public Web2 sources before they are used as
decision-grade evidence.

The source-intelligence layer answers:

    "Which external sources are appropriate candidates for verification?"

It does NOT answer:

    "Is the source absolutely truthful?"

That distinction is fundamental to the Enterprise Intelligence architecture.

Workflow
--------
Candidate Sources
        ↓
Source Intelligence
        ↓
Authority / Provenance / Relevance / Freshness / Corroboration
        ↓
Source Classification
        ↓
Preferred Supported Source
        ↓
FDC / Web2Json
        ↓
Verified External Evidence

The module is deterministic for the prototype so the decision process can
be reproduced from the repository data.

A production implementation can replace the scoring/classification logic
with an LLM-assisted source-analysis layer while preserving the same output
schema and policy boundaries.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SourceClassification(str, Enum):
    PREFERRED = "preferred"
    SECONDARY = "secondary"
    CONTEXT_ONLY = "context_only"
    REJECTED = "reject"


# Lower value = higher priority.
_CLASSIFICATION_PRIORITY = {
    SourceClassification.PREFERRED: 0,
    SourceClassification.SECONDARY: 1,
    SourceClassification.CONTEXT_ONLY: 2,
    SourceClassification.REJECTED: 3,
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SourceCriteria:
    """
    Source-quality dimensions.

    Values are normalized to the range 0.0–1.0.
    """

    authority: float
    provenance: float
    relevance: float
    freshness: float
    corroboration: float

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0"
                )


@dataclass(frozen=True)
class SourceProfile:
    """
    Structured representation of a candidate Web2 source.
    """

    source_id: str
    name: str
    publisher: str
    source_type: str
    url: str

    criteria: SourceCriteria

    supports_web2json: bool = False
    classification: SourceClassification = (
        SourceClassification.CONTEXT_ONLY
    )

    overall_score: float = 0.0
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["classification"] = self.classification.value
        return result


# ---------------------------------------------------------------------------
# Source Intelligence
# ---------------------------------------------------------------------------

class SourceIntelligence:
    """
    Prototype source-intelligence engine.

    It evaluates source characteristics using deterministic scoring.

    The design intentionally exposes the factors used in ranking so that
    a human reviewer can understand why a source was preferred or rejected.
    """

    # Equal weights are deliberately simple for the prototype.
    DEFAULT_WEIGHTS = {
        "authority": 0.20,
        "provenance": 0.20,
        "relevance": 0.20,
        "freshness": 0.20,
        "corroboration": 0.20,
    }

    def __init__(
        self,
        *,
        weights: Optional[Mapping[str, float]] = None,
        preferred_threshold: float = 0.85,
        secondary_threshold: float = 0.70,
        context_threshold: float = 0.50,
    ) -> None:
        self.weights = dict(
            weights
            if weights is not None
            else self.DEFAULT_WEIGHTS
        )

        self._validate_weights()

        self.preferred_threshold = self._validate_threshold(
            preferred_threshold,
            "preferred_threshold",
        )
        self.secondary_threshold = self._validate_threshold(
            secondary_threshold,
            "secondary_threshold",
        )
        self.context_threshold = self._validate_threshold(
            context_threshold,
            "context_threshold",
        )

        if not (
            self.preferred_threshold
            > self.secondary_threshold
            > self.context_threshold
        ):
            raise ValueError(
                "Thresholds must satisfy preferred > secondary > context"
            )

    # ---------------------------------------------------------------------
    # Configuration validation
    # ---------------------------------------------------------------------

    def _validate_weights(self) -> None:
        expected = {
            "authority",
            "provenance",
            "relevance",
            "freshness",
            "corroboration",
        }

        if set(self.weights) != expected:
            raise ValueError(
                "Source weights must contain exactly: "
                + ", ".join(sorted(expected))
            )

        if any(
            not isinstance(value, (int, float))
            or value < 0
            for value in self.weights.values()
        ):
            raise ValueError(
                "Source weights must be non-negative numbers"
            )

        total = sum(self.weights.values())

        if total <= 0:
            raise ValueError(
                "Source weights must have a positive total"
            )

        # Normalize so the caller does not have to supply weights summing
        # exactly to 1.0.
        self.weights = {
            key: value / total
            for key, value in self.weights.items()
        }

    @staticmethod
    def _validate_threshold(
        value: float,
        field_name: str,
    ) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{field_name} must be between 0.0 and 1.0"
            )

        return value

    # ---------------------------------------------------------------------
    # Scoring
    # ---------------------------------------------------------------------

    def calculate_score(
        self,
        criteria: SourceCriteria,
    ) -> float:
        """
        Calculate weighted source suitability score.
        """

        score = (
            criteria.authority
            * self.weights["authority"]
            + criteria.provenance
            * self.weights["provenance"]
            + criteria.relevance
            * self.weights["relevance"]
            + criteria.freshness
            * self.weights["freshness"]
            + criteria.corroboration
            * self.weights["corroboration"]
        )

        return round(score, 4)

    def classify(
        self,
        score: float,
    ) -> SourceClassification:
        """
        Convert a source score into a source classification.
        """

        if score >= self.preferred_threshold:
            return SourceClassification.PREFERRED

        if score >= self.secondary_threshold:
            return SourceClassification.SECONDARY

        if score >= self.context_threshold:
            return SourceClassification.CONTEXT_ONLY

        return SourceClassification.REJECTED

    # ---------------------------------------------------------------------
    # Source analysis
    # ---------------------------------------------------------------------

    def analyze(
        self,
        source: Mapping[str, Any],
    ) -> SourceProfile:
        """
        Analyze one raw source record.

        Expected source structure follows data/sources.json.
        """

        required_fields = [
            "source_id",
            "name",
            "publisher",
            "source_type",
            "url",
        ]

        missing = [
            field
            for field in required_fields
            if field not in source
        ]

        if missing:
            raise ValueError(
                "Source is missing required fields: "
                + ", ".join(missing)
            )

        raw_ai = source.get("ai_assessment", {})

        criteria = SourceCriteria(
            authority=float(
                raw_ai.get("authority", 0.0)
            ),
            provenance=float(
                raw_ai.get("provenance", 0.0)
            ),
            relevance=float(
                raw_ai.get("relevance", 0.0)
            ),
            freshness=float(
                raw_ai.get("freshness", 0.0)
            ),
            corroboration=float(
                raw_ai.get("corroboration", 0.0)
            ),
        )

        score = self.calculate_score(criteria)
        classification = self.classify(score)

        recommendation = self._build_recommendation(
            classification=classification,
            supports_web2json=bool(
                source.get("supports_web2json", False)
            ),
            score=score,
        )

        return SourceProfile(
            source_id=str(source["source_id"]),
            name=str(source["name"]),
            publisher=str(source["publisher"]),
            source_type=str(source["source_type"]),
            url=str(source["url"]),
            criteria=criteria,
            supports_web2json=bool(
                source.get("supports_web2json", False)
            ),
            classification=classification,
            overall_score=score,
            recommendation=recommendation,
        )

    # ---------------------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------------------

    @staticmethod
    def _build_recommendation(
        *,
        classification: SourceClassification,
        supports_web2json: bool,
        score: float,
    ) -> str:
        if classification == SourceClassification.REJECTED:
            return (
                f"Reject for decision-grade evidence "
                f"(source score={score:.2f})."
            )

        if classification == SourceClassification.CONTEXT_ONLY:
            return (
                "Use only as contextual information; "
                "do not rely on it as primary decision evidence."
            )

        if classification == SourceClassification.SECONDARY:
            if supports_web2json:
                return (
                    "Suitable as a secondary evidence source; "
                    "FDC/Web2Json may be considered when supported."
                )

            return (
                "Suitable as secondary/contextual evidence; "
                "not configured for Web2Json in this prototype."
            )

        # Preferred
        if supports_web2json:
            return (
                "Preferred source for decision-grade evidence and "
                "eligible for the Web2Json verification path."
            )

        return (
            "Preferred source by quality assessment, but not configured "
            "for the Web2Json verification path."
        )

    # ---------------------------------------------------------------------
    # Ranking
    # ---------------------------------------------------------------------

    def rank(
        self,
        sources: Iterable[Mapping[str, Any]],
        *,
        require_web2json: bool = False,
    ) -> List[SourceProfile]:
        """
        Analyze and rank candidate sources.

        Ranking priority:
        1. Source classification
        2. Overall source score
        3. Individual source ID for deterministic ordering
        """

        profiles = [
            self.analyze(source)
            for source in sources
        ]

        if require_web2json:
            profiles = [
                profile
                for profile in profiles
                if profile.supports_web2json
            ]

        profiles.sort(
            key=lambda profile: (
                _CLASSIFICATION_PRIORITY[
                    profile.classification
                ],
                -profile.overall_score,
                profile.source_id,
            )
        )

        return profiles

    # ---------------------------------------------------------------------
    # Selection
    # ---------------------------------------------------------------------

    def select(
        self,
        sources: Sequence[Mapping[str, Any]],
        *,
        require_web2json: bool = True,
    ) -> SourceProfile:
        """
        Select the highest-ranked source suitable for the evidence pipeline.

        By default, the selected source must be configured for Web2Json.
        """

        if not sources:
            raise ValueError(
                "No candidate sources were supplied"
            )

        ranked = self.rank(
            sources,
            require_web2json=require_web2json,
        )

        for profile in ranked:
            if profile.classification in {
                SourceClassification.PREFERRED,
                SourceClassification.SECONDARY,
            }:
                return profile

        raise LookupError(
            "No suitable source was found for the evidence workflow"
        )

    # ---------------------------------------------------------------------
    # Multi-source corroboration
    # ---------------------------------------------------------------------

    def corroboration_report(
        self,
        profiles: Sequence[SourceProfile],
    ) -> Dict[str, Any]:
        """
        Build a transparent corroboration summary.

        This does not attempt to prove that independent sources are correct.
        It simply reports the source-quality distribution available to the
        decision pipeline.
        """

        if not profiles:
            return {
                "source_count": 0,
                "preferred_count": 0,
                "secondary_count": 0,
                "context_count": 0,
                "rejected_count": 0,
                "average_score": 0.0,
            }

        counts = {
            SourceClassification.PREFERRED: 0,
            SourceClassification.SECONDARY: 0,
            SourceClassification.CONTEXT_ONLY: 0,
            SourceClassification.REJECTED: 0,
        }

        for profile in profiles:
            counts[profile.classification] += 1

        average_score = sum(
            profile.overall_score
            for profile in profiles
        ) / len(profiles)

        return {
            "source_count": len(profiles),
            "preferred_count": counts[
                SourceClassification.PREFERRED
            ],
            "secondary_count": counts[
                SourceClassification.SECONDARY
            ],
            "context_count": counts[
                SourceClassification.CONTEXT_ONLY
            ],
            "rejected_count": counts[
                SourceClassification.REJECTED
            ],
            "average_score": round(
                average_score,
                4,
            ),
        }


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def analyze_sources(
    sources: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Analyze and return source profiles as dictionaries.
    """

    engine = SourceIntelligence()

    return [
        profile.to_dict()
        for profile in engine.rank(
            list(sources),
            require_web2json=False,
        )
    ]


def select_evidence_source(
    sources: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """
    Select the preferred supported Web2Json source.
    """

    engine = SourceIntelligence()

    selected = engine.select(
        sources,
        require_web2json=True,
    )

    return selected.to_dict()


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_sources = [
        {
            "source_id": "SRC-001",
            "name": "Official Regulatory API",
            "publisher": "Relevant Regulatory Authority",
            "source_type": "regulatory",
            "url": "https://example-regulator.gov/api/entities",
            "supports_web2json": True,
            "ai_assessment": {
                "authority": 0.99,
                "provenance": 0.99,
                "relevance": 0.96,
                "freshness": 0.95,
                "corroboration": 0.94,
            },
        },
        {
            "source_id": "SRC-004",
            "name": "Official Company Website",
            "publisher": "Vendor",
            "source_type": "corporate_website",
            "url": "https://vendor.example.com",
            "supports_web2json": False,
            "ai_assessment": {
                "authority": 0.72,
                "provenance": 0.82,
                "relevance": 0.94,
                "freshness": 0.95,
                "corroboration": 0.61,
            },
        },
        {
            "source_id": "SRC-006",
            "name": "Unknown Industry Website",
            "publisher": "Unverified Publisher",
            "source_type": "industry_website",
            "url": "https://unknown-example.com/company",
            "supports_web2json": False,
            "ai_assessment": {
                "authority": 0.31,
                "provenance": 0.29,
                "relevance": 0.65,
                "freshness": 0.58,
                "corroboration": 0.22,
            },
        },
    ]

    engine = SourceIntelligence()

    profiles = engine.rank(
        demo_sources,
        require_web2json=False,
    )

    print("SOURCE INTELLIGENCE RESULTS")
    print("=" * 60)

    for profile in profiles:
        print(
            f"{profile.source_id} | "
            f"{profile.name} | "
            f"{profile.classification.value.upper()} | "
            f"score={profile.overall_score:.2f}"
        )
        print(f"  {profile.recommendation}")

    print("\nSELECTED EVIDENCE SOURCE")
    print("=" * 60)

    selected = engine.select(
        demo_sources,
        require_web2json=True,
    )

    print(
        f"{selected.name} "
        f"({selected.overall_score:.2f})"
    )

    print("\nCORROBORATION REPORT")
    print("=" * 60)

    report = engine.corroboration_report(profiles)

    for key, value in report.items():
        print(f"{key}: {value}")
