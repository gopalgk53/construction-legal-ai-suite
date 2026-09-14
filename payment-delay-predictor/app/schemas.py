from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# TRAINED CATEGORICAL VOCABULARY
# Logistic Regression v1
# ============================================================

State = Literal[
    "AZ",
    "CA",
    "FL",
    "GA",
    "NC",
    "OTHER",
    "TX",
]

ProjectType = Literal[
    "commercial",
    "industrial",
    "infrastructure",
    "mixed_use",
    "other",
    "residential",
]

PublicPrivate = Literal[
    "private",
    "public",
]

CustomerRole = Literal[
    "equipment_supplier",
    "general_contractor",
    "labor_provider",
    "material_supplier",
    "sub_subcontractor",
    "subcontractor",
]

HiringPartyType = Literal[
    "general_contractor",
    "owner",
    "subcontractor",
]


# ============================================================
# REQUEST
# ============================================================

class PredictionRequest(BaseModel):
    """Validated input for one payment-protection workflow."""

    model_config = ConfigDict(
        extra="forbid"
    )

    state: State
    project_type: ProjectType
    public_private: PublicPrivate
    customer_role: CustomerRole
    hiring_party_type: HiringPartyType

    payment_chain_completeness_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    research_confidence_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    deadline_days_remaining: int

    prior_escalation_rate: float = Field(
        ge=0.0,
        le=1.0,
    )

    prior_projects_with_hiring_party: int = Field(
        ge=0
    )

    expected_party_count: int = Field(
        ge=1
    )

    critical_field_missing: Literal[0, 1]
    multiple_candidate_records: Literal[0, 1]
    conflicting_project_information: Literal[0, 1]


# ============================================================
# EXPLANATION RESPONSE
# ============================================================

class ExplanationFactor(BaseModel):
    feature: str
    label: str

    direction: Literal[
        "higher",
        "lower",
    ]

    contribution_log_odds: float
    absolute_contribution: float
    explanation: str


class PredictionExplanation(BaseModel):
    top_factors: list[ExplanationFactor]
    method: str


# ============================================================
# API RESPONSES
# ============================================================

class PredictionResponse(BaseModel):
    model_version: str

    predicted_operational_risk: float = Field(
        ge=0.0,
        le=1.0,
    )

    threshold: float = Field(
        ge=0.0,
        le=1.0,
    )

    model_decision: Literal[
        "FLAGGED_BY_MODEL",
        "NOT_FLAGGED_BY_MODEL",
    ]

    explanation: PredictionExplanation
    disclaimers: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"]


class ModelMetadataResponse(BaseModel):
    model_version: str
    feature_contract_version: str
    threshold: float
    status: str
