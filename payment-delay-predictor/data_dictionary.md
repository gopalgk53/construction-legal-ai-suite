# Construction Payment Risk Intelligence — Data Dictionary

## Record Grain

One row represents one customer-project payment-protection workflow assessed after initial project research and before the protection workflow is completed.

## Assessment Point

The assessment occurs after initial project intake/research but before future workflow outcomes are known.

Only information available on or before `assessment_date` may be used as model input.

---

# Identifiers

## record_id

Type: string

Example:

`REC-000001`

Purpose:

Unique identifier for each modeling record.

ML usage:

Do NOT use as a model feature.

Reason:

It is only an identifier and contains no meaningful predictive information.

---

## project_id

Type: string

Example:

`PRJ-002341`

Purpose:

Identifies the construction project.

ML usage:

Generally excluded from model training.

Reason:

Raw IDs may cause memorization and provide no generalizable business meaning.

---

## customer_id

Type: string

Example:

`CUS-001245`

Purpose:

Identifies the customer associated with the project workflow.

ML usage:

Do not directly use the raw ID in the first model.

Potential future use:

Historical customer aggregates can be derived using prior records.

---

## assessment_date

Type: date

Purpose:

Defines when the risk assessment is generated.

Critical use:

Controls feature availability and leakage prevention.

---

# Project Features

## state

Type: categorical string

Example values:

- FL
- TX
- CA
- GA
- NC
- AZ
- Other

Purpose:

Represents project jurisdiction/location.

Important:

State itself does not determine risk. It is one contextual feature.

Missing:

No for synthetic v1.

---

## project_type

Type: categorical string

Allowed example values:

- commercial
- residential
- industrial
- infrastructure
- mixed_use
- other

Purpose:

Represents broad project category.

---

## public_private

Type: categorical string

Allowed values:

- public
- private

Purpose:

Represents project ownership/funding classification at a high level.

Important:

This should not be used as a substitute for deterministic legal rules.

---

## project_value_band

Type: categorical string

Allowed values:

- under_100k
- 100k_500k
- 500k_1m
- 1m_5m
- over_5m
- unknown

Purpose:

Represents approximate project scale without pretending exact value is always known.

---

# Customer Contractual Position

## customer_role

Type: categorical string

Allowed values:

- general_contractor
- subcontractor
- sub_subcontractor
- material_supplier
- equipment_supplier
- labor_provider

Purpose:

Describes the customer's functional role in the project.

---

## contractual_tier

Type: integer

Example interpretation:

1 = direct contract with owner

2 = one level below owner

3 = two levels below owner

4 = deeper contractual tier

Purpose:

Represents payment-chain position numerically.

Allowed values:

1–4

---

## hiring_party_type

Type: categorical string

Allowed example values:

- owner
- general_contractor
- subcontractor
- sub_subcontractor
- other

Purpose:

Represents the type of party that directly hired the customer.

---

## distance_from_owner

Type: integer

Purpose:

Approximate number of contractual edges between customer and owner.

Example:

Owner → GC → Supplier

Supplier distance from owner = 2

Allowed values:

0–4

Important:

This is conceptually related to contractual tier, so correlation should be reviewed during EDA.

---

# Payment-Chain Features

## owner_identified

Type: boolean

Values:

0 = no

1 = yes

Purpose:

Indicates whether owner information is available at assessment time.

---

## general_contractor_identified

Type: boolean

Purpose:

Indicates whether the GC has been identified.

---

## hiring_party_identified

Type: boolean

Purpose:

Indicates whether the customer's hiring party is known.

---

## surety_identified

Type: boolean

Purpose:

Indicates whether surety information is available where applicable.

Important:

Not all projects require or contain surety information.

Potential future improvement:

Add `surety_applicable` separately.

---

## lender_identified

Type: boolean

Purpose:

Indicates whether lender information is identified where relevant.

Potential limitation:

Lender availability may vary substantially across project types.

---

## payment_chain_depth

Type: integer

Purpose:

Represents total observed/expected depth of the contractual payment chain.

Example range:

1–5

---

## known_party_count

Type: integer

Purpose:

Number of relevant project parties currently identified.

---

## expected_party_count

Type: integer

Purpose:

Estimated number of relevant project parties expected for the current project structure.

Important:

Must be greater than or equal to `known_party_count`.

---

## payment_chain_completeness_score

Type: float

Range:

0.0–1.0

Formula:

`known_party_count / expected_party_count`

Purpose:

Provides an aggregate representation of payment-chain completeness.

Important:

Keep raw party flags as well as this aggregate.

---

# Project Research Quality

## noc_found

Type: boolean

Purpose:

Indicates whether a relevant Notice of Commencement/reference record was located where applicable to the synthetic workflow.

Important:

This is an information/research field, not a legal conclusion.

---

## owner_match_confidence

Type: float

Range:

0.0–1.0

Purpose:

Represents confidence that researched owner information matches the project.

---

## gc_match_confidence

Type: float

Range:

0.0–1.0

Purpose:

Represents confidence that researched GC information matches the project.

---

## address_match_confidence

Type: float

Range:

0.0–1.0

Purpose:

Represents confidence that the researched address corresponds to the intended project.

---

## multiple_candidate_records

Type: boolean

Purpose:

Indicates whether research returned multiple plausible project records.

---

## conflicting_project_information

Type: boolean

Purpose:

Indicates whether important project information conflicts across sources.

Examples:

- different GC names
- different owner names
- inconsistent addresses
- overlapping project records

---

## research_confidence_score

Type: float

Range:

0.0–1.0

Purpose:

Aggregate estimate of overall research confidence.

Important:

This should not simply duplicate the three individual confidence values exactly.

Synthetic generation should include some additional variation.

---

# Workflow Features

## first_furnishing_date_known

Type: boolean

Purpose:

Indicates whether the relevant first furnishing/service date is available.

---

## notice_required_flag

Type: boolean

Purpose:

Represents the result of a synthetic/validated workflow rule.

Important:

For a real system this should come from maintained deterministic rules, not ML.

---

## deadline_days_remaining

Type: integer

Example range:

-5 to 90

Interpretation:

Positive = days remaining

0 = deadline day

Negative = already past deadline

Purpose:

Operational urgency feature.

Important:

Only use if this value is genuinely known at assessment time.

---

## critical_field_missing

Type: boolean

Purpose:

Indicates whether one or more required workflow fields are missing.

Important:

The definition should be deterministic.

---

# Historical Features

All historical features must use records strictly before the current `assessment_date`.

## prior_projects_with_hiring_party

Type: integer

Range:

0+

Purpose:

Number of prior projects involving the same hiring party.

---

## prior_projects_with_gc

Type: integer

Range:

0+

Purpose:

Number of prior projects involving the same general contractor.

---

## prior_escalation_count

Type: integer

Range:

0+

Purpose:

Number of prior qualifying escalation outcomes.

---

## prior_escalation_rate

Type: float

Range:

0.0–1.0

Purpose:

Historical escalation rate calculated using prior eligible records only.

Important:

Avoid divide-by-zero.

If no prior history exists, use an explicit strategy such as:

- 0 with a separate history-count feature
- missing value
- Bayesian smoothing

Initial synthetic v1:

Use 0 when no historical observations exist while preserving count features.

---

## prior_missing_info_rate

Type: float

Range:

0.0–1.0

Purpose:

Historical frequency of missing-information cases.

---

## prior_manual_review_rate

Type: float

Range:

0.0–1.0

Purpose:

Historical rate at which comparable prior workflows required manual review.

---

# Target

## escalation_required

Type: integer / binary

Values:

0 = workflow completed without entering the defined escalation/manual-risk process

1 = workflow later entered the defined escalation/manual-risk process

Purpose:

Synthetic operational classification target.

Important:

This is NOT:

- a legal determination
- a payment guarantee
- pure payer risk
- a claim recommendation

It represents a synthetic operational escalation outcome for portfolio modeling.

---

# Leakage Policy

Never use fields that occur after the assessment point as model inputs.

Examples of prohibited future features:

- final_claim_status
- final_payment_outcome
- actual_escalation_date
- future_manual_review_result
- final_delivery_result
- future_notice_status

Historical aggregate features must be computed using only records that occurred before the current record.

---

# Initial Modeling Exclusions

The following fields should not be used directly as features:

- record_id
- project_id
- customer_id
- assessment_date

`assessment_date` may later be transformed into safe temporal features if justified.

Examples:

- month
- quarter
- seasonality

but only when there is a defensible reason.

## surety_applicable

Type: boolean

Purpose:

Indicates whether surety information is relevant to the synthetic project workflow.

This prevents `surety_identified = 0` from mixing "not applicable" with "applicable but missing."