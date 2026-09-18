import json

from agent_models import (
    SpecialistResult,
    EvidenceFact,
    EvidenceResult,
    DiscrepancyResult,
    QCResult,
    CorrectionItem,
    CorrectionResult,
)


def extract_json_object(text: str) -> str:
    """
    Extract the first complete JSON object from model output.

    This makes parsing more tolerant if an agent accidentally
    surrounds its JSON with Markdown fences or explanatory text.
    """

    if not isinstance(text, str):
        raise ValueError(
            "Agent output must be a string."
        )

    text = text.strip()

    if not text:
        raise ValueError(
            "Agent returned empty output."
        )

    # Remove common Markdown JSON fences.
    if text.startswith("```json"):
        text = text[len("```json"):].strip()

    elif text.startswith("```"):
        text = text[3:].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    # Find the beginning of the first JSON object.
    start = text.find("{")

    if start == -1:
        raise ValueError(
            "No JSON object found in agent output."
        )

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):

        char = text[index]

        # Handle characters inside JSON strings.
        if in_string:

            if escape:
                escape = False

            elif char == "\\":
                escape = True

            elif char == '"':
                in_string = False

            continue

        # Detect beginning of JSON string.
        if char == '"':
            in_string = True
            continue

        # Track nested JSON objects.
        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return text[start:index + 1]

    raise ValueError(
        "Incomplete JSON object in agent output."
    )


# ============================================================
# SPECIALIST RESULT PARSER
# ============================================================


def parse_specialist_result(
    text: str,
    expected_wo_id: str,
    expected_stage: str,
) -> SpecialistResult:
    """
    Parse and validate a structured specialist-agent result.

    Currently this contract is used by the Research Agent.
    """

    json_text = extract_json_object(text)

    try:
        data = json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Agent returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Specialist result must be a JSON object."
        )

    # --------------------------------------------------------
    # Validate WO ID
    # --------------------------------------------------------

    returned_wo_id = data.get("wo_id")

    if returned_wo_id != expected_wo_id:
        raise ValueError(
            "Agent returned unexpected WO ID. "
            f"Expected {expected_wo_id}, "
            f"received {returned_wo_id}."
        )

    # --------------------------------------------------------
    # Validate stage
    # --------------------------------------------------------

    stage = data.get("stage")

    if stage != expected_stage:
        raise ValueError(
            "Agent returned unexpected stage. "
            f"Expected {expected_stage}, "
            f"received {stage}."
        )

    # --------------------------------------------------------
    # Validate human-review field
    # --------------------------------------------------------

    human_review_required = data.get(
        "human_review_required"
    )

    if not isinstance(
        human_review_required,
        bool,
    ):
        raise ValueError(
            "human_review_required must be a boolean."
        )

    # --------------------------------------------------------
    # Validate recommended next stage
    # --------------------------------------------------------

    recommended_next_stage = data.get(
        "recommended_next_stage"
    )

    if not isinstance(
        recommended_next_stage,
        str,
    ):
        raise ValueError(
            "recommended_next_stage must be a string."
        )

    # Research-specific transition contract.
    #
    # The LLM recommends a stage here.
    # The actual workflow transition is still controlled
    # by deterministic Python in router.py.

    if expected_stage == "RESEARCH":

        allowed_next_stages = {
            "EVIDENCE",
            "HUMAN_REVIEW",
        }

        if (
            recommended_next_stage
            not in allowed_next_stages
        ):
            raise ValueError(
                "Invalid recommended_next_stage "
                "for RESEARCH. "
                f"Received {recommended_next_stage}. "
                "Allowed values: "
                f"{sorted(allowed_next_stages)}"
            )

    # --------------------------------------------------------
    # Validate list-of-string fields
    # --------------------------------------------------------

    list_fields = [
        "material_conflicts",
        "unverified_items",
        "evidence_references",
        "notes",
    ]

    for field_name in list_fields:

        value = data.get(
            field_name,
            [],
        )

        if not isinstance(value, list):
            raise ValueError(
                f"{field_name} must be a list."
            )

        if not all(
            isinstance(item, str)
            for item in value
        ):
            raise ValueError(
                f"Every item in {field_name} "
                "must be a string."
            )

    # --------------------------------------------------------
    # Build SpecialistResult
    # --------------------------------------------------------

    return SpecialistResult(
        wo_id=returned_wo_id,
        stage=stage,
        human_review_required=human_review_required,
        recommended_next_stage=recommended_next_stage,
        material_conflicts=data.get(
            "material_conflicts",
            [],
        ),
        unverified_items=data.get(
            "unverified_items",
            [],
        ),
        evidence_references=data.get(
            "evidence_references",
            [],
        ),
        notes=data.get(
            "notes",
            [],
        ),
    )


# ============================================================
# EVIDENCE RESULT PARSER
# ============================================================


def parse_evidence_result(
    text: str,
    expected_wo_id: str,
) -> EvidenceResult:
    """
    Parse and validate structured Evidence Agent output.

    Unlike the Research result, evidence facts are preserved
    as structured objects rather than flattened strings.
    """

    json_text = extract_json_object(text)

    try:
        data = json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Evidence Agent returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Evidence Agent result must be a JSON object."
        )

    # --------------------------------------------------------
    # Validate WO ID
    # --------------------------------------------------------

    wo_id = data.get("wo_id")

    if wo_id != expected_wo_id:
        raise ValueError(
            "Evidence Agent returned unexpected WO ID. "
            f"Expected {expected_wo_id}, "
            f"received {wo_id}."
        )

    # --------------------------------------------------------
    # Validate stage
    # --------------------------------------------------------

    stage = data.get("stage")

    if stage != "EVIDENCE":
        raise ValueError(
            "Evidence Agent returned invalid stage. "
            f"Expected EVIDENCE, received {stage}."
        )

    # --------------------------------------------------------
    # Validate evidence facts
    # --------------------------------------------------------

    raw_facts = data.get(
        "evidence_facts",
        [],
    )

    if not isinstance(raw_facts, list):
        raise ValueError(
            "evidence_facts must be a list."
        )

    evidence_facts = []

    required_fact_fields = {
        "evidence_id",
        "evidence_type",
        "field",
        "value",
        "source",
        "support_status",
    }

    for index, fact in enumerate(raw_facts):

        if not isinstance(fact, dict):
            raise ValueError(
                f"evidence_facts[{index}] "
                "must be an object."
            )

        missing_fields = (
            required_fact_fields
            - set(fact.keys())
        )

        if missing_fields:
            raise ValueError(
                f"evidence_facts[{index}] "
                "is missing required fields: "
                f"{sorted(missing_fields)}"
            )

        evidence_id = fact["evidence_id"]
        evidence_type = fact["evidence_type"]
        field_name = fact["field"]
        source = fact["source"]
        support_status = fact["support_status"]

        # These provenance fields must always be strings.

        string_fields = {
            "evidence_id": evidence_id,
            "evidence_type": evidence_type,
            "field": field_name,
            "source": source,
            "support_status": support_status,
        }

        for name, value in string_fields.items():

            if not isinstance(value, str):
                raise ValueError(
                    f"evidence_facts[{index}]."
                    f"{name} must be a string."
                )

        evidence_facts.append(
            EvidenceFact(
                evidence_id=evidence_id,
                evidence_type=evidence_type,
                field=field_name,
                value=fact["value"],
                source=source,
                support_status=support_status,
            )
        )

    # --------------------------------------------------------
    # Validate object-list fields
    # --------------------------------------------------------

    object_list_fields = [
        "participants_found",
        "contractual_relationships_supported",
        "confirmations_found",
        "approvals_found",
        "unverified_items",
        "potential_conflicts",
        "evidence_gaps",
    ]

    for field_name in object_list_fields:

        value = data.get(
            field_name,
            [],
        )

        if not isinstance(value, list):
            raise ValueError(
                f"{field_name} must be a list."
            )

        if not all(
            isinstance(item, dict)
            for item in value
        ):
            raise ValueError(
                f"Every item in {field_name} "
                "must be an object."
            )

    # --------------------------------------------------------
    # Validate evidence references
    # --------------------------------------------------------

    evidence_references = data.get(
        "evidence_references",
        [],
    )

    if not isinstance(
        evidence_references,
        list,
    ):
        raise ValueError(
            "evidence_references must be a list."
        )

    if not all(
        isinstance(item, str)
        for item in evidence_references
    ):
        raise ValueError(
            "Every evidence reference "
            "must be a string."
        )

    # --------------------------------------------------------
    # Build EvidenceResult
    # --------------------------------------------------------

    return EvidenceResult(
        wo_id=wo_id,
        stage=stage,
        evidence_facts=evidence_facts,
        participants_found=data.get(
            "participants_found",
            [],
        ),
        contractual_relationships_supported=data.get(
            "contractual_relationships_supported",
            [],
        ),
        confirmations_found=data.get(
            "confirmations_found",
            [],
        ),
        approvals_found=data.get(
            "approvals_found",
            [],
        ),
        unverified_items=data.get(
            "unverified_items",
            [],
        ),
        potential_conflicts=data.get(
            "potential_conflicts",
            [],
        ),
        evidence_gaps=data.get(
            "evidence_gaps",
            [],
        ),
        evidence_references=evidence_references,
    )

def parse_discrepancy_result(
    text: str,
    expected_wo_id: str,
) -> DiscrepancyResult:
    """
    Parse and validate structured Discrepancy Agent output.

    The parser validates the LLM contract.

    It does NOT perform workflow routing.
    """

    json_text = extract_json_object(text)

    try:
        data = json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Discrepancy Agent returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Discrepancy Agent result must be a JSON object."
        )

    # --------------------------------------------------------
    # Validate WO ID
    # --------------------------------------------------------

    wo_id = data.get("wo_id")

    if wo_id != expected_wo_id:
        raise ValueError(
            "Discrepancy Agent returned unexpected WO ID. "
            f"Expected {expected_wo_id}, received {wo_id}."
        )

    # --------------------------------------------------------
    # Validate stage
    # --------------------------------------------------------

    stage = data.get("stage")

    if stage != "DISCREPANCY":
        raise ValueError(
            "Discrepancy Agent returned invalid stage. "
            f"Expected DISCREPANCY, received {stage}."
        )

    # --------------------------------------------------------
    # Validate discrepancy collections
    # --------------------------------------------------------

    classification_fields = {
        "matches": "MATCH",
        "conflicts": "CONFLICT",
        "missing_items": "MISSING",
        "unverified_items": "UNVERIFIED",
    }

    validated_collections = {}

    for field_name, expected_classification in (
        classification_fields.items()
    ):

        items = data.get(
            field_name,
            [],
        )

        if not isinstance(items, list):
            raise ValueError(
                f"{field_name} must be a list."
            )

        for index, item in enumerate(items):

            if not isinstance(item, dict):
                raise ValueError(
                    f"{field_name}[{index}] "
                    "must be an object."
                )

            classification = item.get(
                "classification"
            )

            if classification != expected_classification:
                raise ValueError(
                    f"{field_name}[{index}] has invalid "
                    f"classification {classification}. "
                    f"Expected {expected_classification}."
                )

            if not isinstance(
                item.get("field"),
                str,
            ):
                raise ValueError(
                    f"{field_name}[{index}].field "
                    "must be a string."
                )

            evidence_ids = item.get(
                "evidence_ids",
                [],
            )

            if not isinstance(
                evidence_ids,
                list,
            ):
                raise ValueError(
                    f"{field_name}[{index}]."
                    "evidence_ids must be a list."
                )

            if not all(
                isinstance(value, str)
                for value in evidence_ids
            ):
                raise ValueError(
                    f"Every evidence ID in "
                    f"{field_name}[{index}] "
                    "must be a string."
                )

            reason = item.get(
                "reason"
            )

            if not isinstance(
                reason,
                str,
            ):
                raise ValueError(
                    f"{field_name}[{index}].reason "
                    "must be a string."
                )

        validated_collections[field_name] = items

    # --------------------------------------------------------
    # Validate evidence references
    # --------------------------------------------------------

    evidence_references = data.get(
        "evidence_references",
        [],
    )

    if not isinstance(
        evidence_references,
        list,
    ):
        raise ValueError(
            "evidence_references must be a list."
        )

    for index, reference in enumerate(
        evidence_references
    ):

        if not isinstance(reference, dict):
            raise ValueError(
                f"evidence_references[{index}] "
                "must be an object."
            )

        evidence_id = reference.get(
            "evidence_id"
        )

        if not isinstance(
            evidence_id,
            str,
        ):
            raise ValueError(
                f"evidence_references[{index}]."
                "evidence_id must be a string."
            )

    # --------------------------------------------------------
    # Validate human review recommendation
    # --------------------------------------------------------

    human_review_recommended = data.get(
        "human_review_recommended"
    )

    if not isinstance(
        human_review_recommended,
        bool,
    ):
        raise ValueError(
            "human_review_recommended "
            "must be a boolean."
        )

    # --------------------------------------------------------
    # Validate advisory recommendation
    # --------------------------------------------------------

    recommended_next_stage = data.get(
        "recommended_next_stage"
    )

    if not isinstance(
        recommended_next_stage,
        str,
    ):
        raise ValueError(
            "recommended_next_stage must be a string."
        )

    allowed_recommendations = {
        "QC",
        "HUMAN_REVIEW",
    }

    if (
        recommended_next_stage
        not in allowed_recommendations
    ):
        raise ValueError(
            "Invalid discrepancy "
            "recommended_next_stage. "
            f"Received {recommended_next_stage}. "
            f"Allowed: {sorted(allowed_recommendations)}"
        )

    # --------------------------------------------------------
    # Build result
    # --------------------------------------------------------

    return DiscrepancyResult(
        wo_id=wo_id,
        stage=stage,
        matches=validated_collections[
            "matches"
        ],
        conflicts=validated_collections[
            "conflicts"
        ],
        missing_items=validated_collections[
            "missing_items"
        ],
        unverified_items=validated_collections[
            "unverified_items"
        ],
        evidence_references=evidence_references,
        human_review_recommended=(
            human_review_recommended
        ),
        recommended_next_stage=(
            recommended_next_stage
        ),
    )

def parse_qc_result(raw_text: str, expected_wo_id: str) -> QCResult:
    """
    Parse and validate structured output from the QC Agent.

    The QC Agent performs reasoning, but its output is treated as untrusted
    until it passes this validation layer.

    This function validates:
    - Work Order identity
    - stage
    - QC outcome
    - QC check structure
    - controlled BTP reason codes
    - conflict/unverified structures
    - evidence references
    - human-review flag
    - cross-field consistency rules
    """

    json_text = extract_json_object(raw_text)

    try:
        data = json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"QC Agent returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "QC Agent result must be a JSON object."
        )

    # ---------------------------------------------------------
    # 1. Work Order identity
    # ---------------------------------------------------------

    wo_id = data.get("wo_id")

    if not isinstance(wo_id, str):
        raise ValueError("QC wo_id must be a string")

    if wo_id != expected_wo_id:
        raise ValueError(
            f"QC wo_id mismatch: expected {expected_wo_id}, got {wo_id}"
        )

    # ---------------------------------------------------------
    # 2. Stage
    # ---------------------------------------------------------

    stage = data.get("stage")

    if stage != "QC":
        raise ValueError(
            f"QC stage must be 'QC', got {stage!r}"
        )

    # ---------------------------------------------------------
    # 3. Outcome
    # ---------------------------------------------------------

    allowed_outcomes = {
        "PASS",
        "BTP",
        "HUMAN_REVIEW",
    }

    outcome = data.get("outcome")

    if outcome not in allowed_outcomes:
        raise ValueError(
            f"Invalid QC outcome: {outcome!r}. "
            f"Allowed values: {sorted(allowed_outcomes)}"
        )

    # ---------------------------------------------------------
    # Helper validators
    # ---------------------------------------------------------

    def require_list(value, field_name: str) -> list:
        if not isinstance(value, list):
            raise ValueError(
                f"QC {field_name} must be a list"
            )
        return value

    def require_string(value, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValueError(
                f"QC {field_name} must be a string"
            )
        return value

    def validate_evidence_ids(value, field_name: str) -> list[str]:
        evidence_ids = require_list(value, field_name)

        for evidence_id in evidence_ids:
            if not isinstance(evidence_id, str):
                raise ValueError(
                    f"Every item in QC {field_name} must be a string"
                )

        return evidence_ids

    # ---------------------------------------------------------
    # 4. QC checks
    # ---------------------------------------------------------

    checks = require_list(
        data.get("checks"),
        "checks",
    )

    allowed_check_results = {
        "PASS",
        "FAIL",
        "CONFLICT",
        "MISSING",
        "UNVERIFIED",
        "NOT_APPLICABLE",
    }

    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ValueError(
                f"QC checks[{index}] must be an object"
            )

        require_string(
            check.get("check"),
            f"checks[{index}].check",
        )

        result = check.get("result")

        if result not in allowed_check_results:
            raise ValueError(
                f"Invalid QC checks[{index}].result: {result!r}"
            )

        require_string(
            check.get("reason"),
            f"checks[{index}].reason",
        )

        validate_evidence_ids(
            check.get("evidence_ids"),
            f"checks[{index}].evidence_ids",
        )

    # ---------------------------------------------------------
    # 5. BTP reasons
    # ---------------------------------------------------------

    btp_reasons = require_list(
        data.get("btp_reasons"),
        "btp_reasons",
    )

    allowed_btp_codes = {
        "MISSING_PARTICIPANT",
        "EVIDENCE_MISMATCH",
        "MISSING_CONFIRMATION",
        "DATA_SPELLING_ERROR",
        "PROCESS_FAILURE",
        "CUSTOMER_DATA_MISMATCH",
    }

    for index, reason in enumerate(btp_reasons):
        if not isinstance(reason, dict):
            raise ValueError(
                f"QC btp_reasons[{index}] must be an object"
            )

        code = reason.get("code")

        if code not in allowed_btp_codes:
            raise ValueError(
                f"Invalid QC BTP code at "
                f"btp_reasons[{index}]: {code!r}"
            )

        require_string(
            reason.get("reason"),
            f"btp_reasons[{index}].reason",
        )

        validate_evidence_ids(
            reason.get("evidence_ids"),
            f"btp_reasons[{index}].evidence_ids",
        )

    # ---------------------------------------------------------
    # 6. Material conflicts
    # ---------------------------------------------------------

    material_conflicts = require_list(
        data.get("material_conflicts"),
        "material_conflicts",
    )

    for index, conflict in enumerate(material_conflicts):
        if not isinstance(conflict, dict):
            raise ValueError(
                f"QC material_conflicts[{index}] must be an object"
            )

        validate_evidence_ids(
            conflict.get("evidence_ids"),
            f"material_conflicts[{index}].evidence_ids",
        )

    # ---------------------------------------------------------
    # 7. Unverified items
    # ---------------------------------------------------------

    unverified_items = require_list(
        data.get("unverified_items"),
        "unverified_items",
    )

    for index, item in enumerate(unverified_items):
        if not isinstance(item, dict):
            raise ValueError(
                f"QC unverified_items[{index}] must be an object"
            )

        validate_evidence_ids(
            item.get("evidence_ids"),
            f"unverified_items[{index}].evidence_ids",
        )

    # ---------------------------------------------------------
    # 8. Evidence references
    # ---------------------------------------------------------

    evidence_references = validate_evidence_ids(
        data.get("evidence_references"),
        "evidence_references",
    )

    # ---------------------------------------------------------
    # 9. Human review flag
    # ---------------------------------------------------------

    human_review_required = data.get(
        "human_review_required"
    )

    if not isinstance(human_review_required, bool):
        raise ValueError(
            "QC human_review_required must be a boolean"
        )

    # ---------------------------------------------------------
    # 10. Notes
    # ---------------------------------------------------------

    notes = require_list(
        data.get("notes"),
        "notes",
    )

    for index, note in enumerate(notes):
        require_string(
            note,
            f"notes[{index}]",
        )

    # ---------------------------------------------------------
    # 11. Cross-field safety invariants
    # ---------------------------------------------------------

    if outcome == "PASS":
        if btp_reasons:
            raise ValueError(
                "QC outcome PASS cannot contain BTP reasons"
            )

        if material_conflicts:
            raise ValueError(
                "QC outcome PASS cannot contain material conflicts"
            )

        if human_review_required:
            raise ValueError(
                "QC outcome PASS cannot require human review"
            )

    if outcome == "BTP":
        if not btp_reasons:
            raise ValueError(
                "QC outcome BTP must contain at least one BTP reason"
            )

        if human_review_required:
            raise ValueError(
                "QC outcome BTP cannot simultaneously require "
                "human review"
            )

    if outcome == "HUMAN_REVIEW":
        if not human_review_required:
            raise ValueError(
                "QC outcome HUMAN_REVIEW requires "
                "human_review_required=true"
            )

    # ---------------------------------------------------------
    # 12. Produce trusted application object
    # ---------------------------------------------------------

    return QCResult(
        wo_id=wo_id,
        stage=stage,
        outcome=outcome,
        checks=checks,
        btp_reasons=btp_reasons,
        material_conflicts=material_conflicts,
        unverified_items=unverified_items,
        evidence_references=evidence_references,
        human_review_required=human_review_required,
        notes=notes,
    )

def parse_correction_result(
    raw_text: str,
    expected_wo_id: str,
) -> CorrectionResult:
    """
    Parse and validate Research Correction Agent output.

    The correction agent may propose corrections, but this parser
    does not apply them to the original Work Order.

    Original customer claims remain immutable.
    """

    json_text = extract_json_object(raw_text)

    try:
        data = json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Research Correction Agent returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Research Correction Agent result must be a JSON object."
        )

    # ---------------------------------------------------------
    # Work Order identity
    # ---------------------------------------------------------

    wo_id = data.get("wo_id")

    if not isinstance(wo_id, str):
        raise ValueError(
            "Correction output wo_id must be a string."
        )

    if wo_id != expected_wo_id:
        raise ValueError(
            f"Correction output WO mismatch: "
            f"expected {expected_wo_id!r}, received {wo_id!r}"
        )

    # ---------------------------------------------------------
    # Stage
    # ---------------------------------------------------------

    stage = data.get("stage")

    if stage != "RESEARCH_CORRECTION":
        raise ValueError(
            f"Correction output stage must be "
            f"'RESEARCH_CORRECTION', received {stage!r}"
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def require_list(name: str) -> list:
        value = data.get(name)

        if not isinstance(value, list):
            raise ValueError(
                f"Correction output {name} must be a list."
            )

        return value

    def require_string(
        value,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a string."
            )

        return value

    def validate_evidence_ids(
        value,
        field_name: str,
    ) -> list[str]:
        if not isinstance(value, list):
            raise ValueError(
                f"{field_name} must be a list."
            )

        for index, evidence_id in enumerate(value):
            if not isinstance(evidence_id, str):
                raise ValueError(
                    f"{field_name}[{index}] must be a string."
                )

        return value

    # ---------------------------------------------------------
    # Corrections
    # ---------------------------------------------------------

    corrections_raw = require_list("corrections")

    corrections: list[CorrectionItem] = []

    allowed_resolution_statuses = {
        "PROPOSED",
        "RESOLVED",
        "REJECTED",
    }

    for index, item in enumerate(corrections_raw):

        if not isinstance(item, dict):
            raise ValueError(
                f"corrections[{index}] must be an object."
            )

        field_name = require_string(
            item.get("field"),
            f"corrections[{index}].field",
        )

        # These values may legitimately be strings, numbers,
        # booleans, None, etc., so we intentionally do not
        # restrict their Python type.
        if "original_value" not in item:
            raise ValueError(
                f"corrections[{index}].original_value is required."
            )

        if "proposed_value" not in item:
            raise ValueError(
                f"corrections[{index}].proposed_value is required."
            )

        original_value = item["original_value"]
        proposed_value = item["proposed_value"]

        reason = require_string(
            item.get("reason"),
            f"corrections[{index}].reason",
        )

        evidence_ids = validate_evidence_ids(
            item.get("evidence_ids"),
            f"corrections[{index}].evidence_ids",
        )

        resolution_status = require_string(
            item.get("resolution_status"),
            f"corrections[{index}].resolution_status",
        )

        if resolution_status not in allowed_resolution_statuses:
            raise ValueError(
                f"Invalid corrections[{index}].resolution_status: "
                f"{resolution_status!r}"
            )

        corrections.append(
            CorrectionItem(
                field=field_name,
                original_value=original_value,
                proposed_value=proposed_value,
                reason=reason,
                evidence_ids=evidence_ids,
                resolution_status=resolution_status,
            )
        )

    # ---------------------------------------------------------
    # Unresolved items
    # ---------------------------------------------------------

    unresolved_items = require_list("unresolved_items")

    for index, item in enumerate(unresolved_items):
        if not isinstance(item, dict):
            raise ValueError(
                f"unresolved_items[{index}] must be an object."
            )

    # ---------------------------------------------------------
    # Evidence references
    # ---------------------------------------------------------

    evidence_references = validate_evidence_ids(
        data.get("evidence_references"),
        "evidence_references",
    )

    # ---------------------------------------------------------
    # Human review
    # ---------------------------------------------------------

    human_review_required = data.get(
        "human_review_required"
    )

    if not isinstance(human_review_required, bool):
        raise ValueError(
            "Correction output human_review_required "
            "must be a boolean."
        )

    # ---------------------------------------------------------
    # Notes
    # ---------------------------------------------------------

    notes = require_list("notes")

    for index, note in enumerate(notes):
        if not isinstance(note, str):
            raise ValueError(
                f"notes[{index}] must be a string."
            )

    # ---------------------------------------------------------
    # Safety invariants
    # ---------------------------------------------------------

    if human_review_required:
        if not unresolved_items:
            raise ValueError(
                "Correction output requiring human review "
                "must contain at least one unresolved item."
            )

    for index, correction in enumerate(corrections):

        if correction.original_value == correction.proposed_value:
            raise ValueError(
                f"corrections[{index}] does not actually "
                "change the value."
            )

        if (
            correction.resolution_status == "RESOLVED"
            and not correction.evidence_ids
        ):
            raise ValueError(
                f"corrections[{index}] cannot be RESOLVED "
                "without supporting evidence IDs."
            )

    # ---------------------------------------------------------
    # Build typed result
    # ---------------------------------------------------------

    return CorrectionResult(
        wo_id=wo_id,
        stage=stage,
        corrections=corrections,
        unresolved_items=unresolved_items,
        evidence_references=evidence_references,
        human_review_required=human_review_required,
        notes=notes,
    )