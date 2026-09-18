from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpecialistResult:
    """
    Standard structured result for specialist agents
    that participate in workflow routing.

    The LLM performs reasoning.
    Python uses these fields for deterministic workflow control.
    """

    wo_id: str
    stage: str

    human_review_required: bool = False
    recommended_next_stage: str = ""

    material_conflicts: list[str] = field(
        default_factory=list
    )

    unverified_items: list[str] = field(
        default_factory=list
    )

    evidence_references: list[str] = field(
        default_factory=list
    )

    notes: list[str] = field(
        default_factory=list
    )


@dataclass
class EvidenceFact:
    """
    One atomic fact extracted from an evidence source.
    """

    evidence_id: str
    evidence_type: str
    field: str
    value: Any
    source: str
    support_status: str


@dataclass
class EvidenceResult:
    """
    Structured output produced by the Evidence Agent.

    Evidence describes facts and provenance.
    It does not control workflow routing.
    """

    wo_id: str
    stage: str = "EVIDENCE"

    evidence_facts: list[EvidenceFact] = field(
        default_factory=list
    )

    participants_found: list[dict] = field(
        default_factory=list
    )

    contractual_relationships_supported: list[dict] = field(
        default_factory=list
    )

    confirmations_found: list[dict] = field(
        default_factory=list
    )

    approvals_found: list[dict] = field(
        default_factory=list
    )

    unverified_items: list[dict] = field(
        default_factory=list
    )

    potential_conflicts: list[dict] = field(
        default_factory=list
    )

    evidence_gaps: list[dict] = field(
        default_factory=list
    )

    evidence_references: list[str] = field(
        default_factory=list
    )


@dataclass
class DiscrepancyResult:
    """
    Structured output produced by the Discrepancy Agent.

    The LLM identifies matches, conflicts, missing items,
    and unverified items.

    Python owns the actual workflow transition.
    """

    wo_id: str
    stage: str = "DISCREPANCY"

    matches: list[dict] = field(
        default_factory=list
    )

    conflicts: list[dict] = field(
        default_factory=list
    )

    missing_items: list[dict] = field(
        default_factory=list
    )

    unverified_items: list[dict] = field(
        default_factory=list
    )

    # The real agent returns rich evidence-reference objects,
    # not only evidence-ID strings.
    evidence_references: list[dict] = field(
        default_factory=list
    )

    human_review_recommended: bool = False

    # Advisory only.
    # Python does NOT use this field to execute routing.
    recommended_next_stage: str = ""


@dataclass
class QCResult:
    """
    Structured output produced by the QC Agent.

    The QC Agent may reason about the Work Order, but this object does not
    itself change workflow state. Deterministic Python routing decides what
    happens after QC.
    """

    wo_id: str
    stage: str = "QC"

    # PASS | BTP | HUMAN_REVIEW
    outcome: str = ""

    # Individual QC checks performed by the agent.
    checks: list[dict] = field(default_factory=list)

    # Controlled BTP reasons such as EVIDENCE_MISMATCH.
    btp_reasons: list[dict] = field(default_factory=list)

    # Material conflicts discovered during QC.
    material_conflicts: list[dict] = field(default_factory=list)

    # Items that remain unverified but are not necessarily conflicts.
    unverified_items: list[dict] = field(default_factory=list)

    # IDs of documentary evidence used by QC.
    evidence_references: list[str] = field(default_factory=list)

    # Explicit escalation signal from QC.
    human_review_required: bool = False

    # Non-consequential explanatory notes.
    notes: list[str] = field(default_factory=list)

@dataclass
class CorrectionItem:
    """
    One proposed/resolved correction produced during a BTP cycle.

    The original value is preserved. A correction is represented
    separately so provenance and audit history are not lost.
    """

    field: str
    original_value: Any
    proposed_value: Any
    reason: str
    evidence_ids: list[str] = field(default_factory=list)
    resolution_status: str = "PROPOSED"


@dataclass
class CorrectionResult:
    """
    Structured result of a Research correction cycle.

    This object represents a correction proposal/resolution layer.
    It does not mutate the original synthetic Work Order.
    """

    wo_id: str
    stage: str = "RESEARCH_CORRECTION"
    corrections: list[CorrectionItem] = field(default_factory=list)
    unresolved_items: list[dict] = field(default_factory=list)
    evidence_references: list[str] = field(default_factory=list)
    human_review_required: bool = False
    notes: list[str] = field(default_factory=list)