import pandas as pd
import streamlit as st

from dashboard.services.analytics_service import AnalyticsService
from dashboard.services.risk_queue_service import RiskQueueService
from dashboard.services.workflow_assessment_service import (
    WorkflowAssessmentService,
)
from dashboard.services.human_review_service import (
    HumanReviewService,
)
from dashboard.repositories.human_review_audit_repository import (
    HumanReviewAuditRepository,
)


st.set_page_config(
    page_title="Construction Payment Protection Intelligence",
    page_icon="🏗️",
    layout="wide",
)


@st.cache_resource
def get_analytics_service():
    return AnalyticsService()


@st.cache_resource
def get_risk_queue_service():
    return RiskQueueService()


@st.cache_data(ttl=300)
def load_portfolio_summary():
    return get_analytics_service().get_portfolio_summary()


@st.cache_data(ttl=300)
def load_state_breakdown():
    return get_analytics_service().get_state_breakdown()


@st.cache_data(ttl=300)
def load_risk_queue(limit=25):
    return get_risk_queue_service().build_queue(
        limit=limit
    )


st.title(
    "Construction Payment Protection Intelligence"
)

st.caption(
    "Operational portfolio intelligence for "
    "construction payment-protection workflows."
)


# ---------------------------------------------------------
# PORTFOLIO OVERVIEW
# ---------------------------------------------------------

try:
    summary = load_portfolio_summary()
    states = load_state_breakdown()

except Exception as exc:
    st.error(
        "Portfolio analytics are temporarily unavailable."
    )
    st.exception(exc)
    st.stop()


st.subheader("Portfolio Overview")

row1 = st.columns(4)

row1[0].metric(
    "Total Workflows",
    f"{summary['total_workflows']:,}",
)

row1[1].metric(
    "Avg Chain Completeness",
    f"{summary['avg_chain_completeness']:.1%}",
)

row1[2].metric(
    "Avg Research Confidence",
    f"{summary['avg_research_confidence']:.1%}",
)

row1[3].metric(
    "Deadline ≤ 15 Days",
    f"{summary['deadline_15d_count']:,}",
    delta=(
        f"{summary['deadline_15d_rate']:.1%} "
        "of portfolio"
    ),
    delta_color="off",
)


row2 = st.columns(3)

row2[0].metric(
    "Critical Information Missing",
    f"{summary['critical_missing_count']:,}",
    delta=f"{summary['critical_missing_rate']:.1%}",
    delta_color="off",
)

row2[1].metric(
    "Multiple Candidate Records",
    f"{summary['multiple_candidate_count']:,}",
    delta=f"{summary['multiple_candidate_rate']:.1%}",
    delta_color="off",
)

row2[2].metric(
    "Conflicting Project Information",
    f"{summary['conflicting_info_count']:,}",
    delta=f"{summary['conflicting_info_rate']:.1%}",
    delta_color="off",
)


# ---------------------------------------------------------
# STATE CONTEXT
# ---------------------------------------------------------

st.divider()

st.subheader("State-Level Operational Context")

state_df = pd.DataFrame(states)

if not state_df.empty:
    st.bar_chart(
        state_df.set_index("state")[
            "workflow_count"
        ],
        height=350,
    )

    st.dataframe(
        state_df,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# RISK QUEUE
# ---------------------------------------------------------

st.divider()

st.subheader("Operational Risk Queue")

st.caption(
    "Candidate workflows are selected from Athena "
    "and ranked using the production prediction API."
)

try:
    queue = load_risk_queue(
        limit=25
    )

except Exception as exc:
    st.error(
        "The operational risk queue is temporarily unavailable."
    )
    st.exception(exc)
    queue = []


successful_queue = [
    item
    for item in queue
    if item.get("scoring_status") == "SUCCESS"
]


if successful_queue:

    queue_df = pd.DataFrame(
        successful_queue
    )

    state_options = sorted(
        queue_df["state"]
        .dropna()
        .unique()
    )

    selected_states = st.multiselect(
        "Filter by state",
        options=state_options,
    )

    risk_options = [
        "LOW",
        "MEDIUM",
        "HIGH",
    ]

    selected_bands = st.multiselect(
        "Filter by risk band",
        options=risk_options,
    )

    filtered_df = queue_df.copy()

    if selected_states:
        filtered_df = filtered_df[
            filtered_df["state"].isin(
                selected_states
            )
        ]

    if selected_bands:
        filtered_df = filtered_df[
            filtered_df["risk_band"].isin(
                selected_bands
            )
        ]

    metrics = st.columns(3)

    metrics[0].metric(
        "Queue Workflows",
        len(filtered_df),
    )

    metrics[1].metric(
        "Flagged by Model",
        int(
            (
                filtered_df["model_decision"]
                == "FLAGGED_BY_MODEL"
            ).sum()
        ),
    )

    metrics[2].metric(
        "High Risk Band",
        int(
            (
                filtered_df["risk_band"]
                == "HIGH"
            ).sum()
        ),
    )

    display_queue = filtered_df[
        [
            "record_id",
            "project_id",
            "state",
            "project_type",
            "customer_role",
            "deadline_days_remaining",
            "predicted_operational_risk",
            "risk_band",
            "model_decision",
            "top_factor",
        ]
    ].copy()

    display_queue[
        "predicted_operational_risk"
    ] *= 100

    st.dataframe(
        display_queue,
        use_container_width=True,
        hide_index=True,
    )


    # -----------------------------------------------------
    # SINGLE WORKFLOW ASSESSMENT
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Single Workflow Assessment"
    )

    workflow_options = {
        (
            f"{item['record_id']} | "
            f"{item['project_id']} | "
            f"{item['state']} | "
            f"{item['predicted_operational_risk']:.1%}"
        ):
        item
        for item in successful_queue
    }

    selected_label = st.selectbox(
        "Select workflow for review",
        options=list(
            workflow_options.keys()
        ),
    )

    selected_item = (
        workflow_options[
            selected_label
        ]
    )

    assessment = (
        WorkflowAssessmentService
        .build_assessment(
            selected_item
        )
    )

    risk = assessment[
        "predicted_operational_risk"
    ]

    review_metrics = st.columns(4)

    review_metrics[0].metric(
        "Predicted Risk",
        f"{risk:.1%}",
    )

    review_metrics[1].metric(
        "Risk Band",
        assessment[
            "risk_band"
        ],
    )

    review_metrics[2].metric(
        "Model Threshold",
        f"{assessment['threshold']:.0%}",
    )

    review_metrics[3].metric(
        "Model Decision",
        assessment[
            "model_decision"
        ],
    )


    context_left, context_right = (
        st.columns(2)
    )

    with context_left:

        st.markdown(
            "#### Workflow Context"
        )

        st.write(
            "**Workflow ID:**",
            assessment[
                "workflow_id"
            ],
        )

        st.write(
            "**Project ID:**",
            assessment[
                "project_id"
            ],
        )

        st.write(
            "**State:**",
            assessment[
                "state"
            ],
        )

        st.write(
            "**Project Type:**",
            assessment[
                "project_type"
            ],
        )

        st.write(
            "**Customer Role:**",
            assessment[
                "customer_role"
            ],
        )

        st.write(
            "**Deadline Days Remaining:**",
            assessment[
                "deadline_days_remaining"
            ],
        )


    with context_right:

        st.markdown(
            "#### Model Context"
        )

        st.write(
            "**Model Version:**",
            assessment[
                "model_version"
            ],
        )

        st.write(
            "**Top Model Factor:**",
            assessment[
                "top_factor"
            ],
        )

        st.write(
            "**Factor Explanation:**"
        )

        st.write(
            assessment[
                "top_factor_explanation"
            ]
        )


    # -----------------------------------------------------
    # EXPLAINABILITY UX
    # -----------------------------------------------------

    st.markdown(
        "#### Why was this workflow prioritized?"
    )

    explanation = assessment.get(
        "explanation",
        {}
    )

    factors = explanation.get(
        "top_factors",
        []
    )

    if factors:

        max_strength = max(
            float(
                factor.get(
                    "absolute_contribution",
                    0
                )
            )
            for factor in factors
        )

        for rank, factor in enumerate(
            factors,
            start=1,
        ):

            contribution = float(
                factor.get(
                    "absolute_contribution",
                    0
                )
            )

            if max_strength > 0:
                relative_strength = (
                    contribution
                    / max_strength
                )
            else:
                relative_strength = 0.0

            label = factor.get(
                "label",
                "Model factor"
            )

            direction = factor.get(
                "direction",
                "unknown"
            )

            plain_explanation = (
                factor.get(
                    "explanation",
                    ""
                )
            )

            left, right = st.columns(
                [4, 1]
            )

            with left:
                st.markdown(
                    f"**{rank}. {label}**"
                )

            with right:
                if direction == "higher":
                    st.write(
                        "Higher risk"
                    )

                elif direction == "lower":
                    st.write(
                        "Lower risk"
                    )

                else:
                    st.write(
                        "Model factor"
                    )

            st.progress(
                min(
                    max(
                        relative_strength,
                        0.0,
                    ),
                    1.0,
                )
            )

            st.caption(
                plain_explanation
            )

        st.caption(
            "Bar length represents relative explanation "
            "strength within this prediction. It is not a "
            "probability, causal effect, or legal-risk score."
        )

    else:
        st.info(
            "No model explanation is available "
            "for this workflow."
        )


    # -----------------------------------------------------
    # MODEL DISCLAIMERS
    # -----------------------------------------------------

    disclaimers = assessment.get(
        "disclaimers",
        []
    )

    if disclaimers:

        with st.expander(
            "Model explanation notes"
        ):

            for disclaimer in disclaimers:
                st.write(
                    f"• {disclaimer}"
                )


    # -----------------------------------------------------
    # HUMAN REVIEW
    # -----------------------------------------------------

    st.markdown(
        "#### Human Operational Review"
    )

    st.caption(
        "Record the analyst's operational disposition. "
        "This review is stored separately from the "
        "model prediction and does not overwrite it."
    )

    disposition_labels = {
        "Needs further review":
            "NEEDS_FURTHER_REVIEW",

        "Escalate for operational review":
            "ESCALATE_OPERATIONAL_REVIEW",

        "Insufficient information":
            "INSUFFICIENT_INFORMATION",

        "No further attention":
            "NO_FURTHER_ATTENTION",
    }

    with st.form(
        key=(
            "human_review_form_"
            + assessment["workflow_id"]
        )
    ):

        disposition_label = st.selectbox(
            "Review disposition",
            options=list(
                disposition_labels.keys()
            ),
        )

        review_note = st.text_area(
            "Review note",
            placeholder=(
                "Document the operational reason "
                "for this review disposition."
            ),
            height=120,
        )

        reviewer_id = st.text_input(
            "Reviewer ID",
            value="dashboard-analyst",
        )

        submit_review = st.form_submit_button(
            "Record Human Review"
        )


    if submit_review:

        try:
            review_record = (
                HumanReviewService
                .create_review(
                    assessment=assessment,

                    review_disposition=(
                        disposition_labels[
                            disposition_label
                        ]
                    ),

                    review_note=review_note,

                    reviewer_id=reviewer_id,
                )
            )

        except ValueError as exc:
            st.error(
                str(exc)
            )

        else:
            audit_repository = (
                HumanReviewAuditRepository()
            )

            try:
                persistence = (
                    audit_repository.save_review(
                        review_record
                    )
                )

            except Exception as exc:
                st.error(
                    "The review was created but could "
                    "not be persisted to the audit store."
                )
                st.exception(exc)

            else:
                review_record[
                    "audit_location"
                ] = persistence["key"]

                st.session_state[
                    "latest_human_review"
                ] = review_record

                st.success(
                    "Human operational review recorded "
                    "and persisted to the audit trail."
                )


    latest_review = st.session_state.get(
        "latest_human_review"
    )

    if (
        latest_review
        and latest_review.get(
            "workflow_id"
        )
        == assessment["workflow_id"]
    ):

        with st.expander(
            "Latest Human Review",
            expanded=True,
        ):

            review_cols = st.columns(3)

            review_cols[0].metric(
                "Human Disposition",
                latest_review[
                    "review_disposition"
                ],
            )

            review_cols[1].metric(
                "Model Decision",
                latest_review[
                    "model_decision"
                ],
            )

            review_cols[2].metric(
                "Model Risk",
                (
                    f"{latest_review['predicted_operational_risk']:.1%}"
                ),
            )

            st.write(
                "**Review ID:**",
                latest_review[
                    "review_id"
                ],
            )

            st.write(
                "**Reviewer:**",
                latest_review[
                    "reviewer_id"
                ],
            )

            st.write(
                "**Reviewed At:**",
                latest_review[
                    "reviewed_at"
                ],
            )

            st.write(
                "**Review Note:**",
                latest_review[
                    "review_note"
                ],
            )

            st.caption(
                "The human disposition and model "
                "prediction are separate records. "
                "Human review does not rewrite the "
                "historical model prediction."
            )


    st.warning(
        "The model score and human operational review "
        "support workflow prioritization only. Neither "
        "determines legal rights, notice requirements, "
        "lien rights, bond-claim rights, or payment "
        "outcomes. No external action is triggered "
        "automatically."
    )

else:
    st.info(
        "No successfully scored workflows "
        "are currently available."
    )


# ---------------------------------------------------------
# GOVERNANCE
# ---------------------------------------------------------

st.divider()

st.info(
    "This dashboard supports operational prioritization "
    "and workflow review. Model scores describe learned "
    "associations in synthetic training data. Human review "
    "is required before consequential action."
)
