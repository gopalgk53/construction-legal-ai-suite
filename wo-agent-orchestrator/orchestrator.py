from azure.identity import DefaultAzureCredential


from azure.ai.projects import AIProjectClient


from workflow_state import WorkflowState


from result_parser import (
    parse_specialist_result,
    parse_evidence_result,
    parse_discrepancy_result,
    parse_qc_result,
    parse_correction_result,
)


from router import (
    route_after_research,
    route_after_discrepancy,
    route_after_qc,
    route_after_correction,
)


from correction_overlay import (
    apply_correction_overlay,
    accept_correction_overlay,
    build_effective_correction_context,
)


from observability import (
    configure_logging,
    create_trace_id,
    emit_event,
    StageTimer,
)


# ============================================================


# CONFIGURATION


# ============================================================


PROJECT_ENDPOINT = (
    "https://gopalg53-5366-resource.services.ai.azure.com/" "api/projects/gopalg53-5366"
)


AUTO_APPROVED_MCP_TOOLS = {
    ("sunray-wo-mcp", "get_work_order"),
}


# ============================================================


logger = configure_logging()


# FOUNDRY CLIENT


# ============================================================


credential = DefaultAzureCredential()


project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)


openai_client = project_client.get_openai_client()


# ============================================================


# MCP APPROVAL HANDLING


# ============================================================


def get_mcp_approval_requests(response):

    approval_requests = []

    for item in response.output:

        if getattr(item, "type", None) == "mcp_approval_request":

            approval_requests.append(item)

    return approval_requests


def approve_mcp_requests(
    response,
    agent_name: str,
    agent_version: str,
):

    approval_requests = get_mcp_approval_requests(response)

    if not approval_requests:

        return response

    approval_inputs = []

    for request in approval_requests:

        server_label = getattr(
            request,
            "server_label",
            None,
        )

        tool_name = getattr(
            request,
            "name",
            None,
        )

        tool_identity = (
            server_label,
            tool_name,
        )

        print(f"MCP approval requested: " f"{server_label}.{tool_name}")

        if tool_identity not in AUTO_APPROVED_MCP_TOOLS:

            raise RuntimeError(
                "MCP tool is not approved by local policy: "
                f"{server_label}.{tool_name}"
            )

        print("Approved by synthetic read-only MCP policy.")

        approval_inputs.append(
            {
                "type": "mcp_approval_response",
                "approve": True,
                "approval_request_id": request.id,
            }
        )

    return openai_client.responses.create(
        previous_response_id=response.id,
        input=approval_inputs,
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference",
            }
        },
    )


# ============================================================


# GENERIC AGENT CALL


# ============================================================


def call_agent(
    agent_name: str,
    agent_version: str,
    message: str,
    debug: bool = False,
) -> str:

    print(f"\nCalling {agent_name} " f"v{agent_version}...")

    response = openai_client.responses.create(
        input=[
            {
                "role": "user",
                "content": message,
            }
        ],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference",
            }
        },
    )

    max_approval_rounds = 3

    approval_round = 0

    while get_mcp_approval_requests(response):

        approval_round += 1

        if approval_round > max_approval_rounds:

            raise RuntimeError(
                f"{agent_name}:v{agent_version} exceeded "
                "maximum MCP approval rounds."
            )

        response = approve_mcp_requests(
            response=response,
            agent_name=agent_name,
            agent_version=agent_version,
        )

    if debug:

        print("\n--- DEBUG RESPONSE STATUS ---")

        print(getattr(response, "status", None))

        print("\n--- DEBUG OUTPUT_TEXT ---")

        print(repr(response.output_text))

        print("\n--- DEBUG OUTPUT TYPES ---")

        for item in response.output:

            print(
                " -",
                getattr(
                    item,
                    "type",
                    type(item).__name__,
                ),
            )

    output_text = response.output_text

    if output_text is None or not output_text.strip():

        raise RuntimeError(
            f"{agent_name}:v{agent_version} " "completed without final text output."
        )

    return output_text


# ============================================================


# QC REVIEW


# ============================================================


def run_qc_review(
    state: WorkflowState,
):
    """



    Execute one QC cycle.







    The original Work Order remains immutable.



    Any correction overlay is independently checked by QC.



    """

    print("\n========================================")

    print("STAGE 5 — QC")

    print("========================================")

    correction_context = build_effective_correction_context(state)

    is_correction_rereview = bool(correction_context)

    qc_message = f"""



Perform QC review for this 100% synthetic Work Order:







{state.wo_id}







Independently retrieve the ORIGINAL synthetic Work Order using



the configured get_work_order tool.







The original Work Order is immutable.







--- RESEARCH RESULT ---







{state.research_result}







--- END RESEARCH RESULT ---







--- EVIDENCE RESULT ---







{state.evidence_result}







--- END EVIDENCE RESULT ---







--- DISCREPANCY RESULT ---







{state.discrepancy_result}







--- END DISCREPANCY RESULT ---







--- CORRECTION OVERLAY ---







{correction_context}







--- END CORRECTION OVERLAY ---







CORRECTION RE-REVIEW MODE:







Correction re-review active: {is_correction_rereview}







If correction re-review is active:







1. The ORIGINAL Work Order remains immutable.







2. Do not pretend that the original customer value disappeared.







3. Independently verify each PROPOSED overlay value against the



   ORIGINAL documentary evidence retrieved through get_work_order.







4. If the proposed value is supported by the cited documentary evidence,



   and using that proposed value resolves the specific BTP discrepancy,



   evaluate the Work Order using the EFFECTIVE WORKFLOW VIEW:







       original immutable Work Order



       +



       evidence-supported correction overlay







5. Do NOT return BTP again merely because the immutable original



   customer claim still contains the value that caused the original BTP.







6. If the proposed correction is independently supported and resolves



   the BTP reason, that original discrepancy is considered resolved



   for this QC re-review.







7. If no other BTP reason, material conflict, or human-review condition



   remains, return:







       outcome = "PASS"







8. If the proposed correction is unsupported, contradicted by documentary



   evidence, or does not actually resolve the BTP reason, do NOT PASS.







9. QC does NOT change resolution_status to RESOLVED or ACCEPTED.



   Python owns workflow acceptance after a validated QC PASS.







10. PASS means QC has independently verified the effective workflow view.



    It does NOT mean the original S3 Work Order was modified.







QC RULES:







1. Preserve evidence provenance.







2. CUSTOMER CLAIM and DOCUMENTED EVIDENCE are different fact states.







3. Never silently overwrite customer input.







4. UNVERIFIED does not automatically mean FAIL.







5. MISSING does not automatically mean a required item is missing.







6. Do not create a Bond requirement merely because Bond evidence



   is absent.







7. Do not create a confirmation requirement merely because no



   confirmation exists.







8. Do not create a customer-approval requirement unless the



   established workflow actually requires one.







9. Do not require a signed contract merely because a relationship



   remains UNVERIFIED.







10. Participant identity and contractual relationship are separate.







11. Do not invent legal requirements or deadlines.







12. Do not infer hidden ground truth.







13. Do not search the public web for fictional synthetic identifiers.







CORRECTION OVERLAY RULES:







1. The overlay does NOT modify the original Work Order.







2. Overlay corrections are PROPOSALS.







3. Independently verify every proposed correction against the



   original documentary evidence.







4. Never trust a proposed correction merely because another



   agent generated it.







5. If documentary evidence supports the proposed value, QC may



   evaluate the corrected view using that proposed value.







6. If the proposed correction is unsupported or contradictory,



   do not treat it as resolved.







7. PROPOSED does not automatically mean RESOLVED.







Allowed outcomes:







- PASS



- BTP



- HUMAN_REVIEW







Allowed BTP reason codes:







- MISSING_PARTICIPANT



- EVIDENCE_MISMATCH



- MISSING_CONFIRMATION



- DATA_SPELLING_ERROR



- PROCESS_FAILURE



- CUSTOMER_DATA_MISMATCH







Return ONLY this JSON structure:







{{



  "wo_id": "{state.wo_id}",



  "stage": "QC",



  "outcome": "PASS",



  "checks": [



    {{



      "check": "owner_alignment",



      "result": "PASS",



      "reason": "Customer owner aligns with documentary evidence",



      "evidence_ids": ["E-PC-EXAMPLE"]



    }}



  ],



  "btp_reasons": [],



  "material_conflicts": [],



  "unverified_items": [],



  "evidence_references": [],



  "human_review_required": false,



  "notes": []



}}







STRICT OUTPUT CONTRACT:







wo_id must equal "{state.wo_id}".







stage must be exactly "QC".







outcome must be exactly one of:







- "PASS"



- "BTP"



- "HUMAN_REVIEW"







checks must be a JSON array of objects.







Every checks object must contain:







- check



- result



- reason



- evidence_ids







result must be exactly one of:







- "PASS"



- "FAIL"



- "CONFLICT"



- "MISSING"



- "UNVERIFIED"



- "NOT_APPLICABLE"







evidence_ids must be an array of strings.







btp_reasons must be a JSON array of objects.







Every BTP reason must contain:







- code



- reason



- evidence_ids







code must be exactly one of:







- "MISSING_PARTICIPANT"



- "EVIDENCE_MISMATCH"



- "MISSING_CONFIRMATION"



- "DATA_SPELLING_ERROR"



- "PROCESS_FAILURE"



- "CUSTOMER_DATA_MISMATCH"







material_conflicts must be an array of objects.







unverified_items must be an array of objects.







evidence_references must be an array of STRINGS.







human_review_required must be a JSON boolean.







notes must be an array of STRINGS.







CROSS-FIELD RULES:







If outcome is PASS:







- btp_reasons must be []



- material_conflicts must be []



- human_review_required must be false







If outcome is BTP:







- btp_reasons must contain at least one valid reason



- human_review_required must be false







If outcome is HUMAN_REVIEW:







- human_review_required must be true







Do not return COMPLETE or COMPLETED.







QC provides an assessment only.



Python owns workflow routing.







Do not add extra top-level fields.



Do not use Markdown fences.



Do not include text before or after JSON.



"""

    qc_text = call_agent(
        agent_name="wo-qc-agent",
        agent_version="3",
        message=qc_message,
    )

    qc_parsed = parse_qc_result(
        qc_text,
        expected_wo_id=state.wo_id,
    )

    state.qc_result = qc_text

    state.audit_log.append("QC completed and validated by wo-qc-agent:v3")

    state.audit_log.append(f"QC outcome: {qc_parsed.outcome}")

    qc_route = route_after_qc(qc_parsed)

    state.audit_log.append(f"QC deterministic route: {qc_route}")

    print("\n========================================")

    print("QC ROUTING DECISION")

    print("========================================")

    print("QC outcome:", qc_parsed.outcome)

    print("Route:", qc_route)

    return qc_parsed, qc_route


# ============================================================


# RESEARCH CORRECTION


# ============================================================


def run_research_correction(
    state: WorkflowState,
):
    """



    Research Agent proposes evidence-supported corrections.







    It does NOT modify the original Work Order.



    """

    print("\n========================================")

    print("STAGE 6 — RESEARCH CORRECTION")

    print("========================================")

    correction_message = f"""



Perform RESEARCH CORRECTION for this 100% synthetic Work Order:







{state.wo_id}







QC returned BTP.







--- QC RESULT ---







{state.qc_result}







--- END QC RESULT ---







--- EXISTING CORRECTION OVERLAY ---







{state.correction_overlay}







--- END EXISTING CORRECTION OVERLAY ---







Independently retrieve the ORIGINAL synthetic Work Order using



the configured get_work_order tool.







The original Work Order is immutable.







Your task is to investigate the QC BTP reason and PROPOSE



documentary-evidence-supported corrections.







RULES:







1. Do NOT modify the original Work Order.







2. Do NOT claim that a proposed correction already changed



   the Work Order.







3. Preserve original_value and proposed_value separately.







4. Every proposed correction must include supporting evidence IDs.







5. Do not invent values.







6. Do not infer hidden ground truth.







7. Do not search the public web for fictional synthetic identifiers.







8. CUSTOMER CLAIM and DOCUMENTED EVIDENCE remain separate.







9. If evidence cannot support a safe correction, place the issue



   in unresolved_items and require HUMAN_REVIEW.







10. Every generated correction MUST use:







    "resolution_status": "PROPOSED"







The Research Agent is NOT authorized to mark a correction RESOLVED.







Return ONLY this JSON structure:







{{



  "wo_id": "{state.wo_id}",



  "stage": "RESEARCH_CORRECTION",



  "corrections": [



    {{



      "field": "general_contractor.name",



      "original_value": "Synthetic Original Value",



      "proposed_value": "Synthetic Proposed Value",



      "reason": "Documentary evidence supports proposed value",



      "evidence_ids": [



        "E-NOC-EXAMPLE"



      ],



      "resolution_status": "PROPOSED"



    }}



  ],



  "unresolved_items": [],



  "evidence_references": [],



  "human_review_required": false,



  "notes": []



}}







STRICT OUTPUT CONTRACT:







wo_id must equal "{state.wo_id}".







stage must be exactly:







"RESEARCH_CORRECTION"







corrections must be a JSON array of objects.







Every correction must contain:







- field



- original_value



- proposed_value



- reason



- evidence_ids



- resolution_status







evidence_ids must be an array of strings.







resolution_status MUST be exactly:







"PROPOSED"







Do NOT return RESOLVED.







Do NOT return REJECTED.







original_value and proposed_value must not be equal.







unresolved_items must be an array of objects.







evidence_references must be an array of strings.







human_review_required must be a JSON boolean.







notes must be an array of strings.







If human_review_required is true:







- unresolved_items must contain at least one item.







If you cannot identify a documentary-supported correction:







- corrections must be []



- unresolved_items must explain the issue



- human_review_required must be true







Do not add extra top-level fields.



Do not use Markdown fences.



Do not include text before or after JSON.



"""

    correction_text = call_agent(
        agent_name="wo-research-agent",
        agent_version="5",
        message=correction_message,
    )

    correction_parsed = parse_correction_result(
        correction_text,
        expected_wo_id=state.wo_id,
    )

    state.audit_log.append(
        "RESEARCH_CORRECTION completed and validated " "by wo-research-agent:v5"
    )

    return correction_text, correction_parsed


# ============================================================


# MAIN WORKFLOW


# ============================================================


def emit_workflow_completed(
    *,
    state: WorkflowState,
    trace_id: str,
    workflow_timer: StageTimer,
    status: str,
) -> None:
    """Emit privacy-safe terminal workflow telemetry."""
    emit_event(
        logger,
        event="workflow_completed",
        trace_id=trace_id,
        wo_id=state.wo_id,
        stage=state.current_stage,
        status=status,
        duration_ms=workflow_timer.elapsed_ms(),
        correction_attempt=state.correction_attempts,
        human_review_required=state.human_review_required,
    )


def _run_workflow(
    wo_id: str,
    *,
    trace_id: str,
    workflow_timer: StageTimer,
) -> WorkflowState:

    state = WorkflowState(wo_id=wo_id)


    emit_event(
        logger,
        event="workflow_started",
        trace_id=trace_id,
        wo_id=state.wo_id,
        stage="WORKFLOW",
        status="started",
        correction_attempt=state.correction_attempts,
        human_review_required=state.human_review_required,
    )

    print("\n========================================")

    print("WORK ORDER MULTI-AGENT WORKFLOW")

    print("========================================")

    print("WO ID:", state.wo_id)

    state.audit_log.append(f"Workflow started for {state.wo_id}")

    # ========================================================

    # STAGE 1 — INTAKE

    # ========================================================

    state.current_stage = "INTAKE"

    print("\n========================================")

    print("STAGE 1 — INTAKE")

    print("========================================")

    intake_message = (
        f"Retrieve and analyze synthetic Work Order "
        f"{state.wo_id} using the configured "
        "Work Order retrieval tool."
    )

    state.intake_result = call_agent(
        agent_name="wo-intake-agent",
        agent_version="3",
        message=intake_message,
    )

    state.audit_log.append("INTAKE completed by wo-intake-agent:v3")

    # ========================================================

    # STAGE 2 — RESEARCH

    # ========================================================

    state.current_stage = "RESEARCH"

    print("\n========================================")

    print("STAGE 2 — RESEARCH")

    print("========================================")

    research_message = f"""



Perform RESEARCH for this 100% synthetic Work Order:







{state.wo_id}







--- INTAKE RESULT ---







{state.intake_result}







--- END INTAKE RESULT ---







Independently retrieve and inspect the synthetic Work Order using



the configured get_work_order tool.







RULES:







1. Preserve evidence provenance.



2. Distinguish CUSTOMER CLAIM from DOCUMENTED EVIDENCE.



3. UNVERIFIED does not mean CONFLICT.



4. UNVERIFIED does not automatically require human review.



5. MISSING does not mean REQUIRED MISSING.



6. Keep participant identity separate from contractual relationship.



7. Do not invent legal requirements or deadlines.



8. Do not search the public web for fictional synthetic identifiers.



9. Recommend HUMAN_REVIEW only for a material conflict or an



   unresolved consequential issue supported by available evidence.







Return ONLY:







{{



  "wo_id": "{state.wo_id}",



  "stage": "RESEARCH",



  "human_review_required": false,



  "recommended_next_stage": "EVIDENCE",



  "material_conflicts": [],



  "unverified_items": [],



  "evidence_references": [],



  "notes": []



}}







STRICT CONTRACT:







- stage exactly "RESEARCH"



- recommended_next_stage only "EVIDENCE" or "HUMAN_REVIEW"



- material_conflicts: array of strings



- unverified_items: array of strings



- evidence_references: array of strings



- notes: array of strings



- no Markdown



- no additional text



"""

    state.research_result = call_agent(
        agent_name="wo-research-agent",
        agent_version="5",
        message=research_message,
    )

    research_parsed = parse_specialist_result(
        state.research_result,
        expected_wo_id=state.wo_id,
        expected_stage="RESEARCH",
    )

    state.audit_log.append(
        "RESEARCH completed and validated by " "wo-research-agent:v5"
    )

    research_route = route_after_research(research_parsed)

    state.audit_log.append(f"RESEARCH deterministic route: {research_route}")

    print("\n========================================")

    print("RESEARCH ROUTING DECISION")

    print("========================================")

    print("Route:", research_route)

    if research_route == "HUMAN_REVIEW":

        state.current_stage = "HUMAN_REVIEW"

        state.human_review_required = True

        state.audit_log.append("Workflow escalated to HUMAN_REVIEW after RESEARCH")

        emit_workflow_completed(
            state=state,
            trace_id=trace_id,
            workflow_timer=workflow_timer,
            status="human_review",
        )

        return state

    # ========================================================

    # STAGE 3 — EVIDENCE

    # ========================================================

    state.current_stage = "EVIDENCE"

    state.audit_log.append("Workflow advanced to EVIDENCE")

    print("\n========================================")

    print("STAGE 3 — EVIDENCE")

    print("========================================")

    evidence_message = f"""



Perform EVIDENCE analysis for this 100% synthetic Work Order:







{state.wo_id}







--- RESEARCH RESULT ---







{state.research_result}







--- END RESEARCH RESULT ---







Independently retrieve the original synthetic Work Order using



get_work_order.







RULES:







1. Original Work Order is immutable.



2. Preserve evidence provenance.



3. Separate CUSTOMER CLAIM from DOCUMENTED EVIDENCE.



4. Never silently overwrite customer claims.



5. Participant identity and contractual relationship are separate.



6. UNVERIFIED does not mean CONFLICT.



7. MISSING does not automatically mean required missing.



8. Do not invent legal requirements or deadlines.



9. Do not infer hidden ground truth.



10. Do not search the public web for synthetic identifiers.







Return ONLY:







{{



  "wo_id": "{state.wo_id}",



  "stage": "EVIDENCE",



  "evidence_facts": [],



  "participants_found": [],



  "contractual_relationships_supported": [],



  "confirmations_found": [],



  "approvals_found": [],



  "unverified_items": [],



  "potential_conflicts": [],



  "evidence_gaps": [],



  "evidence_references": []



}}







Every evidence_facts object must contain:







- evidence_id



- evidence_type



- field



- value



- source



- support_status







participants_found,



contractual_relationships_supported,



confirmations_found,



approvals_found,



unverified_items,



potential_conflicts,



evidence_gaps







must each be arrays of objects.







evidence_references must be an array of strings.







No Markdown.



No additional text.



"""

    state.evidence_result = call_agent(
        agent_name="wo-evidence-agent",
        agent_version="3",
        message=evidence_message,
    )

    evidence_parsed = parse_evidence_result(
        state.evidence_result,
        expected_wo_id=state.wo_id,
    )

    state.audit_log.append(
        "EVIDENCE completed and validated by " "wo-evidence-agent:v3"
    )

    state.audit_log.append(
        f"EVIDENCE facts validated: " f"{len(evidence_parsed.evidence_facts)}"
    )

    state.audit_log.append(
        f"EVIDENCE potential conflicts: " f"{len(evidence_parsed.potential_conflicts)}"
    )

    # ========================================================

    # STAGE 4 — DISCREPANCY

    # ========================================================

    state.current_stage = "DISCREPANCY"

    state.audit_log.append("Workflow advanced to DISCREPANCY")

    print("\n========================================")

    print("STAGE 4 — DISCREPANCY")

    print("========================================")

    discrepancy_message = f"""



Perform DISCREPANCY analysis for this 100% synthetic Work Order:







{state.wo_id}







--- RESEARCH RESULT ---







{state.research_result}







--- END RESEARCH RESULT ---







--- EVIDENCE RESULT ---







{state.evidence_result}







--- END EVIDENCE RESULT ---







Independently retrieve the original synthetic Work Order using



get_work_order.







RULES:







1. Preserve provenance.



2. Never silently overwrite customer claims.



3. CUSTOMER CLAIM and DOCUMENTED EVIDENCE are different.



4. UNVERIFIED is NOT CONFLICT.



5. UNVERIFIED is NOT automatically MISSING.



6. MISSING is NOT automatically REQUIRED MISSING.



7. An evidence gap is not automatically a discrepancy.



8. Do not infer Bond requirements merely because Bond is absent.



9. Do not infer confirmation requirements merely because no



   confirmation exists.



10. Do not infer customer approval requirements unless established.



11. Participant identity and contractual relationship are separate.



12. Do not invent legal requirements or deadlines.



13. Do not infer hidden ground truth.



14. Do not search the web for fictional synthetic identifiers.







Return ONLY:







{{



  "wo_id": "{state.wo_id}",



  "stage": "DISCREPANCY",



  "matches": [],



  "conflicts": [],



  "missing_items": [],



  "unverified_items": [],



  "evidence_references": [],



  "human_review_recommended": false,



  "recommended_next_stage": "QC"



}}







STRICT CLASSIFICATION CONTRACT:







Every object in matches MUST contain:







"classification": "MATCH"







Every object in conflicts MUST contain:







"classification": "CONFLICT"







Every object in missing_items MUST contain:







"classification": "MISSING"







Every object in unverified_items MUST contain:







"classification": "UNVERIFIED"







Never omit classification.







Each classification object should contain:







- classification



- field



- customer_value



- evidence_value



- reason



- evidence_ids







evidence_references must be an array of objects.







Example:







{{



  "evidence_id": "E-PC-EXAMPLE",



  "evidence_type": "PROPERTY_CARD"



}}







human_review_recommended must be boolean.







recommended_next_stage must be:







- "QC"



or



- "HUMAN_REVIEW"







The recommendation is advisory only.



Python owns routing.







No Markdown.



No additional text.



"""

    state.discrepancy_result = call_agent(
        agent_name="wo-discrepancy-agent",
        agent_version="3",
        message=discrepancy_message,
    )

    discrepancy_parsed = parse_discrepancy_result(
        state.discrepancy_result,
        expected_wo_id=state.wo_id,
    )

    state.audit_log.append(
        "DISCREPANCY completed and validated by " "wo-discrepancy-agent:v3"
    )

    state.audit_log.append(
        f"DISCREPANCY conflicts detected: " f"{len(discrepancy_parsed.conflicts)}"
    )

    state.audit_log.append(
        f"DISCREPANCY missing items: " f"{len(discrepancy_parsed.missing_items)}"
    )

    discrepancy_route = route_after_discrepancy(discrepancy_parsed)

    state.audit_log.append(f"DISCREPANCY deterministic route: " f"{discrepancy_route}")

    print("\n========================================")

    print("DISCREPANCY ROUTING DECISION")

    print("========================================")

    print("Route:", discrepancy_route)

    if discrepancy_route == "HUMAN_REVIEW":

        state.current_stage = "HUMAN_REVIEW"

        state.human_review_required = True

        state.audit_log.append(
            "Workflow escalated to HUMAN_REVIEW " "after DISCREPANCY"
        )

        emit_workflow_completed(
            state=state,
            trace_id=trace_id,
            workflow_timer=workflow_timer,
            status="human_review",
        )

        return state

    # ========================================================

    # STAGE 5/6 — QC + CORRECTION LOOP

    # ========================================================

    state.current_stage = "QC"

    state.audit_log.append("Workflow advanced to QC")

    while True:

        # ----------------------------------------------------

        # QC

        # ----------------------------------------------------

        qc_parsed, qc_route = run_qc_review(state)

        # ----------------------------------------------------

        # PASS

        # ----------------------------------------------------

        if qc_route == "COMPLETE_RECOMMENDED":

            # ------------------------------------------------

            # DETERMINISTIC CORRECTION ACCEPTANCE

            # ------------------------------------------------

            #

            # If this PASS occurred after a correction cycle,

            # QC has independently evaluated the proposed

            # correction against documentary evidence.

            #

            # Python—not the Research Agent and not the QC

            # Agent—owns workflow acceptance.

            #

            # This changes only the workflow overlay.

            # The original S3 Work Order remains immutable.

            proposed_fields = [
                item["field"]
                for item in state.correction_overlay
                if item.get("resolution_status") == "PROPOSED"
            ]

            for field in proposed_fields:

                accept_correction_overlay(
                    state=state,
                    field=field,
                )

                state.audit_log.append(
                    f"Python accepted correction overlay " f"after QC PASS: {field}"
                )

            state.current_stage = "COMPLETE_RECOMMENDED"

            state.audit_log.append("Workflow reached COMPLETE_RECOMMENDED")

            emit_workflow_completed(
                state=state,
                trace_id=trace_id,
                workflow_timer=workflow_timer,
                status="complete_recommended",
            )

            return state

            # ----------------------------------------------------

        # HUMAN REVIEW

        # ----------------------------------------------------

        if qc_route == "HUMAN_REVIEW":

            state.current_stage = "HUMAN_REVIEW"

            state.human_review_required = True

            state.audit_log.append("Workflow escalated to HUMAN_REVIEW after QC")

            emit_workflow_completed(
                state=state,
                trace_id=trace_id,
                workflow_timer=workflow_timer,
                status="human_review",
            )

            return state

        # ----------------------------------------------------

        # BTP

        # ----------------------------------------------------

        if qc_route != "RESEARCH_CORRECTION":

            raise RuntimeError(f"Unexpected QC route: {qc_route!r}")

        state.current_stage = "RESEARCH_CORRECTION"

        state.audit_log.append("Workflow routed to RESEARCH_CORRECTION " "after QC BTP")

        # ----------------------------------------------------

        # RESEARCH CORRECTION

        # ----------------------------------------------------

        correction_text, correction_parsed = run_research_correction(state)

        # ----------------------------------------------------

        # DETERMINISTIC CORRECTION ROUTING

        # ----------------------------------------------------

        correction_route = route_after_correction(
            result=correction_parsed,
            state=state,
        )

        state.audit_log.append(
            f"RESEARCH_CORRECTION deterministic route: " f"{correction_route}"
        )

        print("\n========================================")

        print("RESEARCH CORRECTION RESULT")

        print("========================================")

        print(correction_text)

        print("\n========================================")

        print("RESEARCH CORRECTION ROUTING DECISION")

        print("========================================")

        print("Route:", correction_route)

        print(
            "Correction attempts:",
            state.correction_attempts,
        )

        # ----------------------------------------------------

        # HUMAN REVIEW / RETRY LIMIT

        # ----------------------------------------------------

        if correction_route == "HUMAN_REVIEW":

            state.current_stage = "HUMAN_REVIEW"

            state.human_review_required = True

            state.audit_log.append(
                "Workflow escalated to HUMAN_REVIEW " "after RESEARCH_CORRECTION"
            )

            emit_workflow_completed(
                state=state,
                trace_id=trace_id,
                workflow_timer=workflow_timer,
                status="human_review",
            )

            return state

        if correction_route != "QC_REVIEW":

            raise RuntimeError(
                "Unexpected Research Correction route: " f"{correction_route!r}"
            )

        # ----------------------------------------------------

        # NON-DESTRUCTIVE CORRECTION OVERLAY

        # ----------------------------------------------------

        apply_correction_overlay(
            state=state,
            result=correction_parsed,
        )

        state.audit_log.append(
            f"Correction overlay size: " f"{len(state.correction_overlay)}"
        )

        # ----------------------------------------------------

        # QC RE-REVIEW

        # ----------------------------------------------------

        state.current_stage = "QC"

        state.audit_log.append(
            "Workflow returned to QC for independent " "correction re-review"
        )

        # while loop now executes QC again.

        # ============================================================


# MAIN


# ============================================================

def run_workflow(
    wo_id: str,
) -> WorkflowState:
    """
    Public workflow execution boundary.

    Creates execution-level observability context and guarantees
    privacy-safe failure telemetry for every caller, including
    CLI, tests, APIs, and future service integrations.
    """
    trace_id = create_trace_id()
    workflow_timer = StageTimer()

    try:
        return _run_workflow(
            wo_id=wo_id,
            trace_id=trace_id,
            workflow_timer=workflow_timer,
        )

    except Exception as exc:
        emit_event(
            logger,
            event="workflow_failed",
            trace_id=trace_id,
            wo_id=wo_id,
            stage="WORKFLOW",
            status="failed",
            duration_ms=workflow_timer.elapsed_ms(),
            error_type=type(exc).__name__,
        )

        raise



if __name__ == "__main__":

    # Step 19E:

    # Synthetic Work Order intentionally containing the

    # customer/documentary GC-name discrepancy.

    #

    # Original S3 record remains immutable.

    WO_ID = "SYN-WO-000111"

    try:

        state = run_workflow(WO_ID)

        # ====================================================

        # RESULTS

        # ====================================================

        print("\n========================================")

        print("INTAKE RESULT")

        print("========================================")

        print(state.intake_result)

        print("\n========================================")

        print("RESEARCH RESULT")

        print("========================================")

        print(state.research_result)

        print("\n========================================")

        print("EVIDENCE RESULT")

        print("========================================")

        print(state.evidence_result)

        print("\n========================================")

        print("DISCREPANCY RESULT")

        print("========================================")

        print(state.discrepancy_result)

        print("\n========================================")

        print("LATEST QC RESULT")

        print("========================================")

        print(state.qc_result)

        # ====================================================

        # SUMMARY

        # ====================================================

        print("\n========================================")

        print("WORKFLOW SUMMARY")

        print("========================================")

        print(
            "WO ID:",
            state.wo_id,
        )

        print(
            "Current stage:",
            state.current_stage,
        )

        print(
            "Human review required:",
            state.human_review_required,
        )

        print(
            "Correction attempts:",
            state.correction_attempts,
        )

        print(
            "Correction overlay items:",
            len(state.correction_overlay),
        )

        if state.correction_overlay:

            print("\nCorrection overlay:")

            for item in state.correction_overlay:

                print(
                    " -",
                    item,
                )

        print("\nAudit log:")

        for entry in state.audit_log:

            print(
                " -",
                entry,
            )

    except Exception as exc:

        print("\n========================================")

        print("WORKFLOW FAILED")

        print("========================================")

        print(
            "Error type:",
            type(exc).__name__,
        )

        print(
            "Error:",
            str(exc),
        )

        raise
