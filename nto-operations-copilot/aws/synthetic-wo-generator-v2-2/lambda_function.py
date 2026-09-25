import boto3
import json
import os
import random
import copy
from datetime import date, timedelta
from collections import Counter


# ============================================================
# AWS / DATASET CONFIGURATION
# ============================================================

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["SYNTHETIC_BUCKET"]

SEED = 42
DATASET_VERSION = "2.2"
DATASET_PATH_VERSION = "v2.2"
TOTAL_WOS = 220


# ============================================================
# SYNTHETIC MASTER DATA
# ============================================================

COMPANY_PREFIXES = [
    "Blue Harbor",
    "Silver Oak",
    "Northstar",
    "Evergreen",
    "Redwood",
    "Clearwater",
    "Sunset Ridge",
    "Ironwood",
    "Cedar Point",
    "Horizon",
    "Riverstone",
    "Pinecrest",
]


COMPANY_SUFFIXES = [
    "Builders LLC",
    "Construction LLC",
    "Development Group LLC",
    "Property Holdings LLC",
    "Contracting LLC",
    "Supply Company LLC",
]


STREETS = [
    "Innovation Avenue",
    "Example Boulevard",
    "Prototype Drive",
    "Simulation Lane",
    "Test Harbor Road",
    "Model Creek Way",
    "Synthetic Park Drive",
    "Demo Ridge Boulevard",
]


CITIES = [
    "Demo City",
    "Example Bay",
    "Prototype Beach",
    "Synthetic Springs",
    "Model Harbor",
    "Test Valley",
]


WORK_TYPES = [
    "BUILDING_MATERIAL_SUPPLY",
    "ELECTRICAL_MATERIAL_SUPPLY",
    "PLUMBING_MATERIAL_SUPPLY",
    "ROOFING_MATERIAL_SUPPLY",
    "HVAC_MATERIAL_SUPPLY",
    "CONSTRUCTION_SERVICES",
]


ENTRY_PATHS = [
    ("JOB_INFORMATION_SHEET", "MANUAL_ENTRY"),
    ("EXCEL", "JSON_IMPORT"),
    ("INVOICE", "DOCUMENT_PARSER"),
]


# ============================================================
# SCENARIO CATALOG
# ============================================================

SCENARIOS = [
    ("PRIVATE_RESIDENTIAL_CLEAN", "PRIVATE_RESIDENTIAL"),
    ("PRIVATE_RESIDENTIAL_NOC_MISSING", "PRIVATE_RESIDENTIAL"),
    ("PRIVATE_RESIDENTIAL_OWNER_CONFLICT", "PRIVATE_RESIDENTIAL"),
    ("PRIVATE_RESIDENTIAL_GC_CONFLICT", "PRIVATE_RESIDENTIAL"),
    ("PRIVATE_RESIDENTIAL_PARTICIPANT_MISSING", "PRIVATE_RESIDENTIAL"),

    ("PRIVATE_COMMERCIAL_CLEAN", "PRIVATE_COMMERCIAL"),
    ("PRIVATE_COMMERCIAL_NOC_MISSING", "PRIVATE_COMMERCIAL"),
    ("PRIVATE_COMMERCIAL_OWNER_CONFLICT", "PRIVATE_COMMERCIAL"),
    ("PRIVATE_COMMERCIAL_GC_CONFLICT", "PRIVATE_COMMERCIAL"),
    ("PRIVATE_COMMERCIAL_EXTRA_PARTICIPANTS", "PRIVATE_COMMERCIAL"),
    ("PRIVATE_COMMERCIAL_LEASEHOLD", "PRIVATE_COMMERCIAL"),
    ("PRIVATE_COMMERCIAL_CONFIRMATION_REQUIRED", "PRIVATE_COMMERCIAL"),

    ("COUNTY_PUBLIC_BOND_FOUND", "STATE_COUNTY"),
    ("COUNTY_PUBLIC_BOND_MISSING", "STATE_COUNTY"),
    ("COUNTY_PUBLIC_BOND_CONFIRMED", "STATE_COUNTY"),
    ("COUNTY_PUBLIC_NO_RESPONSE", "STATE_COUNTY"),

    ("MUNICIPAL_BOND_FOUND", "TOWN_MUNICIPALITY"),
    ("MUNICIPAL_BOND_MISSING", "TOWN_MUNICIPALITY"),
    ("MUNICIPAL_CUSTOMER_APPROVAL", "TOWN_MUNICIPALITY"),

    ("FEDERAL_BOND_FOUND", "FEDERAL"),
    ("FEDERAL_BOND_MISSING", "FEDERAL"),
    ("FEDERAL_CUSTOMER_APPROVAL", "FEDERAL"),

    ("QC_EVIDENCE_MISMATCH", "PRIVATE_COMMERCIAL"),
    ("QC_BTP_CORRECTION", "PRIVATE_RESIDENTIAL"),
]

# Customer-intake teaching cases requested for the research coach.
# Five deterministic variants of each family add 100 new records.
ADDITIONAL_SCENARIOS = [
    ("INTAKE_NOC_PROVIDED_CLEAN", "PRIVATE_RESIDENTIAL"),
    ("INTAKE_NOC_NOT_PROVIDED_FOUND", "PRIVATE_RESIDENTIAL"),
    ("INTAKE_NOC_NOT_PROVIDED_MISSING", "PRIVATE_COMMERCIAL"),
    ("INTAKE_NOC_PROVIDED_GC_CONFLICT", "PRIVATE_COMMERCIAL"),
    ("INTAKE_BOND_PROVIDED_CLEAN", "STATE_COUNTY"),
    ("INTAKE_BOND_NOT_PROVIDED_FOUND", "TOWN_MUNICIPALITY"),
    ("INTAKE_BOND_NOT_PROVIDED_MISSING", "FEDERAL"),
    ("INTAKE_BOND_PROVIDED_GC_CONFLICT", "STATE_COUNTY"),
    ("INTAKE_ADDRESS_COMPLETE", "PRIVATE_RESIDENTIAL"),
    ("INTAKE_ADDRESS_INCOMPLETE", "PRIVATE_COMMERCIAL"),
    ("INTAKE_ADDRESS_MISMATCH", "PRIVATE_COMMERCIAL"),
    ("INTAKE_GC_PROVIDED_CLEAN", "PRIVATE_RESIDENTIAL"),
    ("INTAKE_GC_NOT_PROVIDED", "PRIVATE_COMMERCIAL"),
    ("INTAKE_SUBCONTRACTOR_ONLY", "PRIVATE_COMMERCIAL"),
    ("INTAKE_DIRECT_OWNER_LABELED_GC", "PRIVATE_RESIDENTIAL"),
    ("INTAKE_DIRECT_OWNER_CORRECT_ROLE", "PRIVATE_RESIDENTIAL"),
    ("INTAKE_NOC_PROVIDED_NO_GC", "PRIVATE_COMMERCIAL"),
    ("INTAKE_BOND_PROVIDED_NO_GC", "TOWN_MUNICIPALITY"),
    ("INTAKE_NOC_AND_ADDRESS_MISSING", "PRIVATE_RESIDENTIAL"),
    ("INTAKE_OWNER_BUILDER_ROLE_UNCLEAR", "PRIVATE_RESIDENTIAL"),
]


# ============================================================
# HELPERS
# ============================================================

def synthetic_company(rng, suffix=None):
    prefix = rng.choice(COMPANY_PREFIXES)

    if suffix:
        return f"{prefix} {suffix}"

    return f"{prefix} {rng.choice(COMPANY_SUFFIXES)}"


def synthetic_address(rng, index):
    return {
        "street": f"{1000 + index} {rng.choice(STREETS)}",
        "city": rng.choice(CITIES),
        "state": "FL",
        "zip": f"{32000 + (index % 700):05d}",
    }


def make_participant(
    pid,
    role,
    name,
    source,
    verified,
):
    return {
        "participant_id": pid,
        "role": role,
        "name": name,
        "source": source,
        "verification_status": verified,
    }


# ============================================================
# SYNTHETIC EVIDENCE FACT GENERATORS
# ============================================================

def make_property_card_facts(
    index,
    owner_name,
    project_address,
):
    """
    Synthetic Property Card facts.

    Represents facts a researcher could extract from
    county/property records.

    All values are synthetic.
    """

    return {
        "record_type": "PROPERTY_CARD",

        "parcel_or_folio": f"SYN-FOLIO-{index:06d}",

        "owner": {
            "name": owner_name,
            "verification_status": "DOCUMENTED",
        },

        "property_address": copy.deepcopy(project_address),

        "legal_description": (
            f"SYNTHETIC LOT {index:03d} "
            f"BLOCK {(index % 20) + 1}"
        ),

        "record_source": "SYNTHETIC_COUNTY_RECORD",

        "synthetic": True,
    }


def make_noc_facts(
    index,
    owner_name,
    gc_name,
    project_address,
    additional_participants=None,
):
    """
    Synthetic Notice of Commencement facts.
    """

    return {
        "record_type": "NOC",

        "instrument_number":
            f"SYN-INST-{index:06d}",

        "noc_reference":
            f"SYN-NOC-{index:06d}",

        "owner": {
            "name": owner_name,
        },

        "general_contractor": {
            "name": gc_name,
        },

        "project_address":
            copy.deepcopy(project_address),

        "additional_participants":
            copy.deepcopy(additional_participants or []),

        "record_source":
            "SYNTHETIC_OFFICIAL_RECORD",

        "synthetic": True,
    }


def make_permit_facts(
    index,
    owner_name,
    gc_name,
    project_address,
):
    """
    Synthetic Permit/supporting-record facts.

    Permit is modeled as supporting evidence,
    not as a universal legal requirement.
    """

    return {
        "record_type": "PERMIT",

        "permit_number":
            f"SYN-PERMIT-{index:06d}",

        "owner": {
            "name": owner_name,
        },

        "contractor": {
            "name": gc_name,
        },

        "project_address":
            copy.deepcopy(project_address),

        "record_source":
            "SYNTHETIC_PERMIT_RECORD",

        "synthetic": True,
    }


def make_bond_facts(
    index,
    owner_name,
    gc_name,
    project_address,
    bond_company,
    surety_agent,
):
    """
    Synthetic payment Bond facts for public-project
    research scenarios.
    """

    return {
        "record_type": "BOND",

        "bond_number":
            f"SYN-BOND-{index:06d}",

        "instrument_number":
            f"SYN-BOND-INST-{index:06d}",

        "owner": {
            "name": owner_name,
        },

        "general_contractor": {
            "name": gc_name,
        },

        "bond_company": {
            "name": bond_company,
        },

        "surety_agent": {
            "name": surety_agent,
        },

        "project_address":
            copy.deepcopy(project_address),

        "record_source":
            "SYNTHETIC_BOND_RECORD",

        "synthetic": True,
    }


# ============================================================
# WORK ORDER GENERATOR
# ============================================================

def generate_work_order(
    index,
    scenario_name,
    project_type,
):

    rng = random.Random(SEED + index)

    wo_id = f"SYN-WO-{index:06d}"
    scenario_id = f"SYN-SCENARIO-{index:03d}"

    source_type, ingestion_method = ENTRY_PATHS[
        (index - 1) % len(ENTRY_PATHS)
    ]

    # --------------------------------------------------------
    # CUSTOMER CLAIMS
    # --------------------------------------------------------

    owner_claimed = synthetic_company(
        rng,
        "Property Holdings LLC",
    )

    gc_claimed = synthetic_company(
        rng,
        "Builders LLC",
    )

    # Preserve the correctly documented GC before introducing
    # any customer-side correction scenario.
    gc_documented_target = gc_claimed

    # --------------------------------------------------------
    # V2.1: QC BTP CUSTOMER-DATA DEFECT
    # --------------------------------------------------------
    #
    # This is deliberately visible to the agents.
    #
    # Customer claim:
    #     Example Builder LLC
    #
    # Documentary evidence:
    #     Example Builders LLC
    #
    # The expected BTP answer remains evaluator-only.
    # --------------------------------------------------------

    if scenario_name == "QC_BTP_CORRECTION":

        if gc_claimed.endswith("Builders LLC"):
            gc_claimed = gc_claimed.replace(
                "Builders LLC",
                "Builder LLC",
            )
        else:
            gc_claimed = (
                f"{gc_claimed} Typo"
            )

    customer_company = synthetic_company(
        rng,
        "Supply Company LLC",
    )

    project_address = synthetic_address(
        rng,
        index,
    )

    customer_job_address = copy.deepcopy(project_address)
    if "ADDRESS_INCOMPLETE" in scenario_name:
        customer_job_address["street"] = None
        customer_job_address["zip"] = None
    if "ADDRESS_MISMATCH" in scenario_name:
        customer_job_address["street"] = f"{9000 + index} Customer Claim Road"
    if "ADDRESS_MISSING" in scenario_name:
        customer_job_address = None

    if "DIRECT_OWNER_LABELED_GC" in scenario_name:
        gc_claimed = owner_claimed

    first_day = (
        date(2026, 1, 1)
        + timedelta(
            days=(index * 3) % 240
        )
    ).isoformat()

    job_amount = rng.randrange(
        5000,
        250000,
        500,
    )

    # --------------------------------------------------------
    # CUSTOMER-CLAIM PARTICIPANTS
    # --------------------------------------------------------

    participants = [
        make_participant(
            "P-001",
            "OWNER",
            owner_claimed,
            "CUSTOMER_INPUT",
            "UNVERIFIED",
        ),
        make_participant(
            "P-002",
            "GENERAL_CONTRACTOR",
            gc_claimed,
            "CUSTOMER_INPUT",
            "UNVERIFIED",
        ),
    ]

    contractual_chain = [
        {
            "from_participant": "P-001",
            "to_participant": "P-002",
            "relationship": "OWNER_TO_GC",
            "verification_status": "UNVERIFIED",
        }
    ]

    evidence = []
    discrepancies = []
    communications = []
    approvals = []

    research_status = "UNDER_REVIEW"

    qc_status = "PASS"
    btp_reasons = []

    expected_action = "PROCEED_TO_QC"

    correction_history = []

    # --------------------------------------------------------
    # PREPARE RESEARCHED VALUES
    # --------------------------------------------------------

    evidence_owner = owner_claimed

    if scenario_name == "QC_BTP_CORRECTION":
        evidence_gc = gc_documented_target
    else:
        evidence_gc = gc_claimed

    # --------------------------------------------------------
    # STANDARD OWNER CONFLICT
    # --------------------------------------------------------

    if "OWNER_CONFLICT" in scenario_name:

        evidence_owner = synthetic_company(
            rng,
            "Property Holdings LLC",
        )

        if evidence_owner == owner_claimed:
            evidence_owner = (
                f"Alternate Synthetic Owner "
                f"{index} LLC"
            )

    # --------------------------------------------------------
    # STANDARD GC CONFLICT
    # --------------------------------------------------------

    if "GC_CONFLICT" in scenario_name:

        evidence_gc = synthetic_company(
            rng,
            "Construction LLC",
        )

        if evidence_gc == gc_claimed:
            evidence_gc = (
                f"Alternate Synthetic Contractor "
                f"{index} LLC"
            )

    if "PROVIDED_GC_CONFLICT" in scenario_name:
        evidence_gc = synthetic_company(rng, "Construction LLC")
        if evidence_gc == gc_claimed:
            evidence_gc = f"Alternate Synthetic Contractor {index} LLC"

    # --------------------------------------------------------
    # V2.1:
    # INDEPENDENT DOCUMENTARY SOURCES
    # --------------------------------------------------------
    #
    # Earlier v2 used one evidence_gc value for both NOC
    # and Permit. That made QC_EVIDENCE_MISMATCH impossible
    # to represent in the agent-visible evidence.
    #
    # v2.1 gives each documentary source independent values.
    # --------------------------------------------------------

    noc_owner = evidence_owner
    noc_gc = evidence_gc

    permit_owner = evidence_owner
    permit_gc = evidence_gc

    # --------------------------------------------------------
    # V2.1: QC DOCUMENTARY EVIDENCE MISMATCH
    # --------------------------------------------------------
    #
    # Customer and NOC agree.
    # Permit deliberately disagrees.
    #
    # The agent must discover this mismatch from evidence.
    # --------------------------------------------------------

    if scenario_name == "QC_EVIDENCE_MISMATCH":

        permit_gc = synthetic_company(
            rng,
            "Construction LLC",
        )

        if permit_gc == noc_gc:
            permit_gc = (
                f"Alternate Synthetic Permit "
                f"Contractor {index} LLC"
            )

    # ========================================================
    # PRIVATE PROJECT EVIDENCE
    # ========================================================

    if project_type in [
        "PRIVATE_RESIDENTIAL",
        "PRIVATE_COMMERCIAL",
    ]:

        property_card_facts = (
            make_property_card_facts(
                index=index,
                owner_name=evidence_owner,
                project_address=project_address,
            )
        )

        noc_additional_participants = []

        # ----------------------------------------------------
        # EXTRA PARTICIPANTS
        # ----------------------------------------------------

        if "EXTRA_PARTICIPANTS" in scenario_name:

            noc_additional_participants.extend(
                [
                    {
                        "role":
                            "DESIGNATED_RECIPIENT",

                        "name":
                            (
                                f"Synthetic Designated "
                                f"Recipient {index}"
                            ),
                    },
                    {
                        "role":
                            "LENDER",

                        "name":
                            (
                                f"Synthetic Lender "
                                f"{index} LLC"
                            ),
                    },
                ]
            )

        # ----------------------------------------------------
        # LEASEHOLD
        # ----------------------------------------------------

        if "LEASEHOLD" in scenario_name:

            noc_additional_participants.extend(
                [
                    {
                        "role":
                            "TENANT",

                        "name":
                            (
                                f"Synthetic Tenant "
                                f"{index} LLC"
                            ),
                    },
                    {
                        "role":
                            "LEASEHOLD",

                        "name":
                            (
                                f"Synthetic Leasehold "
                                f"{index} LLC"
                            ),
                    },
                ]
            )

        # ----------------------------------------------------
        # CREATE NOC
        # ----------------------------------------------------

        noc_facts = make_noc_facts(
            index=index,
            owner_name=noc_owner,
            gc_name=noc_gc,
            project_address=project_address,
            additional_participants=
                noc_additional_participants,
        )

        # ----------------------------------------------------
        # CREATE PERMIT
        # ----------------------------------------------------

        permit_facts = make_permit_facts(
            index=index,
            owner_name=permit_owner,
            gc_name=permit_gc,
            project_address=project_address,
        )

        # ----------------------------------------------------
        # PROPERTY CARD
        # ----------------------------------------------------

        evidence.append(
            {
                "evidence_id":
                    f"E-PC-{index:06d}",

                "type":
                    "PROPERTY_CARD",

                "status":
                    "FOUND",

                "source":
                    "SYNTHETIC_COUNTY_RECORD",

                "supports": [
                    "OWNER",
                    "LEGAL_DESCRIPTION",
                    "FOLIO",
                ],

                "extracted_facts":
                    property_card_facts,
            }
        )

        # ----------------------------------------------------
        # NOC
        # ----------------------------------------------------

        evidence.append(
            {
                "evidence_id":
                    f"E-NOC-{index:06d}",

                "type":
                    "NOC",

                "status":
                    "FOUND",

                "source":
                    "SYNTHETIC_OFFICIAL_RECORD",

                "supports": [
                    "OWNER",
                    "GENERAL_CONTRACTOR",
                ],

                "extracted_facts":
                    noc_facts,
            }
        )

        # ----------------------------------------------------
        # PERMIT
        # ----------------------------------------------------

        evidence.append(
            {
                "evidence_id":
                    f"E-PERMIT-{index:06d}",

                "type":
                    "PERMIT",

                "status":
                    "FOUND",

                "source":
                    "SYNTHETIC_PERMIT_RECORD",

                "supports": [
                    "OWNER",
                    "GENERAL_CONTRACTOR",
                    "PROJECT_ADDRESS",
                ],

                "extracted_facts":
                    permit_facts,
            }
        )

    # ========================================================
    # PUBLIC PROJECT / BOND EVIDENCE
    # ========================================================

    if project_type in [
        "STATE_COUNTY",
        "TOWN_MUNICIPALITY",
        "FEDERAL",
    ]:

        bond_company = synthetic_company(
            rng,
            "Surety Company",
        )

        surety_agent = (
            f"Synthetic Surety Agent {index}"
        )

        bond_facts = make_bond_facts(
            index=index,
            owner_name=evidence_owner,
            gc_name=evidence_gc,
            project_address=project_address,
            bond_company=bond_company,
            surety_agent=surety_agent,
        )

        evidence.append(
            {
                "evidence_id":
                    f"E-BOND-{index:06d}",

                "type":
                    "BOND",

                "status":
                    "FOUND",

                "source":
                    "SYNTHETIC_BOND_RECORD",

                "supports": [
                    "OWNER",
                    "GENERAL_CONTRACTOR",
                    "BOND_COMPANY",
                    "BOND_NUMBER",
                    "SURETY_AGENT",
                ],

                "extracted_facts":
                    bond_facts,
            }
        )

    # ========================================================
    # SCENARIO BEHAVIOR
    # ========================================================

    # --------------------------------------------------------
    # MISSING NOC
    # --------------------------------------------------------

    if "NOC_MISSING" in scenario_name:

        for item in evidence:
            if item["type"] == "NOC":
                item["status"] = "NOT_FOUND"

        discrepancies.append(
            "MISSING_EVIDENCE"
        )

        communications.append(
            {
                "type":
                    "EMAIL",

                "recipient_role":
                    "CUSTOMERS_CUSTOMER",

                "outcome":
                    "CONFIRMED",

                "synthetic":
                    True,
            }
        )

        expected_action = (
            "USE_CONFIRMATION_PATH"
        )

    if "NOC_NOT_PROVIDED_MISSING" in scenario_name:
        for item in evidence:
            if item["type"] == "NOC":
                item["status"] = "NOT_FOUND"
        discrepancies.append("MISSING_EVIDENCE")
        research_status = "ON_HOLD"
        expected_action = "USE_CONFIRMATION_PATH"

    # --------------------------------------------------------
    # OWNER CONFLICT
    # --------------------------------------------------------

    if "OWNER_CONFLICT" in scenario_name:

        participants.append(
            make_participant(
                "P-003",
                "OWNER",
                evidence_owner,
                "PROPERTY_CARD",
                "VERIFIED",
            )
        )

        discrepancies.append(
            "OWNER_CONFLICT"
        )

        expected_action = (
            "FLAG_OWNER_DISCREPANCY"
        )

    # --------------------------------------------------------
    # GC CONFLICT
    # --------------------------------------------------------

    if "GC_CONFLICT" in scenario_name:

        participants.append(
            make_participant(
                "P-003",
                "GENERAL_CONTRACTOR",
                evidence_gc,
                "NOC",
                "VERIFIED",
            )
        )

        discrepancies.append(
            "GC_CONFLICT"
        )

        expected_action = (
            "FLAG_GC_DISCREPANCY"
        )

    # --------------------------------------------------------
    # MISSING PARTICIPANT
    # --------------------------------------------------------

    if "PARTICIPANT_MISSING" in scenario_name:

        discrepancies.append(
            "MISSING_PARTICIPANT"
        )

        qc_status = "FAIL"

        btp_reasons.append(
            "MISSING_PARTICIPANT"
        )

        expected_action = (
            "BTP_TO_RESEARCH"
        )

    # --------------------------------------------------------
    # EXTRA NOC PARTICIPANTS
    # --------------------------------------------------------

    if "EXTRA_PARTICIPANTS" in scenario_name:

        participants.extend(
            [
                make_participant(
                    "P-003",
                    "DESIGNATED_RECIPIENT",
                    synthetic_company(rng),
                    "NOC",
                    "VERIFIED",
                ),
                make_participant(
                    "P-004",
                    "LENDER",
                    synthetic_company(rng),
                    "NOC",
                    "VERIFIED",
                ),
            ]
        )

    # --------------------------------------------------------
    # LEASEHOLD / TENANT
    # --------------------------------------------------------

    if "LEASEHOLD" in scenario_name:

        participants.extend(
            [
                make_participant(
                    "P-003",
                    "TENANT",
                    synthetic_company(rng),
                    "NOC",
                    "VERIFIED",
                ),
                make_participant(
                    "P-004",
                    "LEASEHOLD",
                    synthetic_company(rng),
                    "NOC",
                    "VERIFIED",
                ),
            ]
        )

        expected_action = (
            "REVIEW_LEASEHOLD_PARTICIPANTS"
        )

    # --------------------------------------------------------
    # PRIVATE CONFIRMATION
    # --------------------------------------------------------

    if "CONFIRMATION_REQUIRED" in scenario_name:

        communications.append(
            {
                "type":
                    "CALL",

                "recipient_role":
                    "CUSTOMERS_CUSTOMER",

                "outcome":
                    "CONFIRMED",

                "synthetic":
                    True,
            }
        )

        expected_action = (
            "USE_CONFIRMATION_PATH"
        )

    # --------------------------------------------------------
    # PUBLIC BOND MISSING
    # --------------------------------------------------------

    if "BOND_MISSING" in scenario_name:

        for item in evidence:
            if item["type"] == "BOND":
                item["status"] = "NOT_FOUND"

        discrepancies.append(
            "MISSING_EVIDENCE"
        )

        communications.append(
            {
                "type":
                    "EMAIL",

                "recipient_role":
                    "CUSTOMERS_CUSTOMER",

                "outcome":
                    "PENDING",

                "synthetic":
                    True,
            }
        )

        research_status = "ON_HOLD"

        expected_action = (
            "SEEK_BOND_CONFIRMATION"
        )

    if "BOND_NOT_PROVIDED_MISSING" in scenario_name:
        for item in evidence:
            if item["type"] == "BOND":
                item["status"] = "NOT_FOUND"
        discrepancies.append("MISSING_EVIDENCE")
        research_status = "ON_HOLD"
        expected_action = "SEEK_BOND_CONFIRMATION"

    if "ADDRESS_INCOMPLETE" in scenario_name or "ADDRESS_MISMATCH" in scenario_name or "ADDRESS_MISSING" in scenario_name:
        discrepancies.append("JOB_ADDRESS_REQUIRES_VERIFICATION")
        expected_action = "VERIFY_PROPERTY_BEFORE_RESEARCH"

    if "GC_NOT_PROVIDED" in scenario_name or "NO_GC" in scenario_name or "SUBCONTRACTOR_ONLY" in scenario_name:
        participants[:] = [item for item in participants if item["source"] != "CUSTOMER_INPUT" or item["role"] != "GENERAL_CONTRACTOR"]
        discrepancies.append("CUSTOMER_GC_MISSING")
        expected_action = "VERIFY_CONTRACTUAL_CHAIN"

    if "DIRECT_OWNER_LABELED_GC" in scenario_name:
        discrepancies.append("CUSTOMER_ROLE_MISMATCH")
        expected_action = "VERIFY_DIRECT_TO_OWNER_RELATIONSHIP"

    if "DIRECT_OWNER_CORRECT_ROLE" in scenario_name:
        contractual_chain[:] = [{
            "from_participant": "P-001",
            "to_participant": "CUSTOMER",
            "relationship": "OWNER_TO_CUSTOMER",
            "verification_status": "UNVERIFIED",
        }]
        expected_action = "VERIFY_DIRECT_TO_OWNER_RELATIONSHIP"

    if "OWNER_BUILDER_ROLE_UNCLEAR" in scenario_name:
        discrepancies.append("OWNER_BUILDER_ROLE_UNCLEAR")
        research_status = "ON_HOLD"
        expected_action = "VERIFY_OWNER_BUILDER_STATUS"

    # Intake queue records have not yet been researched. Scenario-specific
    # discrepancies and expected actions remain in evaluator-only ground truth.
    if scenario_name.startswith("INTAKE_"):
        research_status = "READY_FOR_RESEARCH"

    # --------------------------------------------------------
    # BOND CONFIRMED
    # --------------------------------------------------------

    if "BOND_CONFIRMED" in scenario_name:

        communications.append(
            {
                "type":
                    "CALL",

                "recipient_role":
                    "CUSTOMERS_CUSTOMER",

                "outcome":
                    "CONFIRMED",

                "synthetic":
                    True,
            }
        )

        expected_action = (
            "RECORD_BOND_CONFIRMATION"
        )

    # --------------------------------------------------------
    # NO RESPONSE
    # --------------------------------------------------------

    if "NO_RESPONSE" in scenario_name:

        for item in evidence:
            if item["type"] == "BOND":
                item["status"] = "NOT_FOUND"

        communications.append(
            {
                "type":
                    "EMAIL",

                "recipient_role":
                    "CUSTOMERS_CUSTOMER",

                "outcome":
                    "NO_RESPONSE",

                "synthetic":
                    True,
            }
        )

        research_status = "ON_HOLD"

        expected_action = (
            "REQUEST_CUSTOMER_APPROVAL"
        )

    # --------------------------------------------------------
    # CUSTOMER APPROVAL
    # --------------------------------------------------------

    if "CUSTOMER_APPROVAL" in scenario_name:

        for item in evidence:
            if item["type"] == "BOND":
                item["status"] = "NOT_FOUND"

        communications.append(
            {
                "type":
                    "CALL",

                "recipient_role":
                    "CUSTOMERS_CUSTOMER",

                "outcome":
                    "NO_RESPONSE",

                "synthetic":
                    True,
            }
        )

        approvals.append(
            {
                "approval_type":
                    "PROCEED_WITHOUT_BOND",

                "status":
                    "RECEIVED",

                "synthetic":
                    True,
            }
        )

        expected_action = (
            "PROCEED_WITH_CUSTOMER_APPROVAL"
        )

    # --------------------------------------------------------
    # V2.1 QC EVIDENCE MISMATCH
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # The actual mismatch has already been placed in the
    # agent-visible Permit facts above.
    #
    # Everything below is evaluator-only expected behavior.
    # --------------------------------------------------------

    if scenario_name == "QC_EVIDENCE_MISMATCH":

        discrepancies.append(
            "EVIDENCE_MISMATCH"
        )

        qc_status = "FAIL"

        btp_reasons.append(
            "EVIDENCE_MISMATCH"
        )

        expected_action = (
            "BTP_TO_RESEARCH"
        )

    # --------------------------------------------------------
    # V2.1 QC BTP CORRECTION
    # --------------------------------------------------------
    #
    # The actual customer-data mismatch was created before
    # the customer participant objects were built.
    #
    # Documentary evidence retains the correct GC value.
    # --------------------------------------------------------

    if scenario_name == "QC_BTP_CORRECTION":

        discrepancies.append(
            "CUSTOMER_DATA_MISMATCH"
        )

        qc_status = "FAIL"

        btp_reasons.append(
            "CUSTOMER_DATA_MISMATCH"
        )

        correction_history.append(
            {
                "sequence":
                    1,

                "qc_result":
                    "FAIL",

                "btp_reason":
                    "CUSTOMER_DATA_MISMATCH",
            }
        )

        correction_history.append(
            {
                "sequence":
                    2,

                "research_action":
                    "CORRECTED",

                "qc_result":
                    "PASS",
            }
        )

        expected_action = (
            "BTP_TO_RESEARCH"
        )

    # --------------------------------------------------------
    # BOND PARTICIPANTS
    # --------------------------------------------------------

    if any(
        item["type"] == "BOND"
        and item["status"] == "FOUND"
        for item in evidence
    ):

        participants.extend(
            [
                make_participant(
                    "P-BOND-001",
                    "BOND_COMPANY",
                    synthetic_company(rng),
                    "BOND",
                    "VERIFIED",
                ),
                make_participant(
                    "P-SURETY-001",
                    "SURETY_AGENT",
                    "Synthetic Surety Agent",
                    "BOND",
                    "VERIFIED",
                ),
            ]
        )

    # ========================================================
    # CANONICAL WORK ORDER
    # ========================================================

    return {
        "metadata": {
            "synthetic":
                True,

            "dataset_version":
                DATASET_VERSION,

            "generator_seed":
                SEED,

            "scenario_id":
                scenario_id,

            "scenario_family":
                scenario_name,

            "wo_id":
                wo_id,
        },

        "customer_input": {
            "source_type":
                source_type,

            "ingestion_method":
                ingestion_method,

            "customer": {
                "name":
                    customer_company,
            },

            "job": {
                "job_name":
                    f"Synthetic Project {index:03d}",

                "job_address":
                    copy.deepcopy(customer_job_address),

                "project_type_claimed":
                    project_type,

                "type_of_work":
                    rng.choice(WORK_TYPES),

                "first_day_on_job":
                    first_day,

                "job_amount":
                    job_amount,
            },

            "customer_customer": {
                "name":
                    (owner_claimed if "DIRECT_OWNER_CORRECT_ROLE" in scenario_name else None if "GC_NOT_PROVIDED" in scenario_name or "NO_GC" in scenario_name else gc_claimed),

                "role_claimed":
                    ("OWNER" if "DIRECT_OWNER_CORRECT_ROLE" in scenario_name else "SUBCONTRACTOR" if "SUBCONTRACTOR_ONLY" in scenario_name else "GENERAL_CONTRACTOR"),

                "email":
                    f"contact{index}@example.invalid",

                "phone":
                    f"+1-555-{1000 + index:04d}",
            },

            "claimed_participants": [
                {
                    "role":
                        "OWNER",

                    "name":
                        owner_claimed,
                },
                {
                    "role":
                        ("SUBCONTRACTOR" if "SUBCONTRACTOR_ONLY" in scenario_name else "GENERAL_CONTRACTOR"),

                    "name":
                        gc_claimed,
                },
            ] if "GC_NOT_PROVIDED" not in scenario_name and "NO_GC" not in scenario_name else [
                {"role": "OWNER", "name": owner_claimed}
            ],

            "provided_references": {
                "permit_number":
                    f"SYN-PERMIT-{index:06d}",

                "noc_reference":
                    (f"SYN-NOC-{index:06d}" if "NOC_PROVIDED" in scenario_name or not scenario_name.startswith("INTAKE_") else None),

                "parcel_or_folio":
                    f"SYN-FOLIO-{index:06d}",

                "bond_number":
                    (
                        f"SYN-BOND-{index:06d}"
                        if project_type in [
                            "STATE_COUNTY",
                            "TOWN_MUNICIPALITY",
                            "FEDERAL",
                        ] and ("BOND_PROVIDED" in scenario_name or not scenario_name.startswith("INTAKE_"))
                        else None
                    ),
            },
        },

        "project": {
            "classified_type":
                project_type,

            "classification_status":
                "SYNTHETIC_GROUND_TRUTH",
        },

        "participants":
            participants,

        "contractual_chain":
            contractual_chain,

        "evidence":
            evidence,

        "communications":
            communications,

        "customer_approvals":
            approvals,

        "research": {
            "status":
                research_status,

            "discrepancies":
                discrepancies,
        },

        "qc": {
            "status":
                qc_status,

            "btp_reasons":
                btp_reasons,

            "correction_history":
                correction_history,
        },

        "ground_truth": {
            "expected_project_type":
                project_type,

            "expected_discrepancies":
                copy.deepcopy(discrepancies),

            "expected_research_action":
                expected_action,

            "expected_qc_outcome":
                qc_status,

            "expected_requires_human_review":
                (
                    research_status == "ON_HOLD"
                ),
        },
    }


# ============================================================
# AGENT / EVALUATOR SEPARATION
# ============================================================

def create_agent_input(wo):
    """
    Creates the version of a Work Order that an AI agent
    is allowed to see.

    Evaluator answers are removed.
    """

    agent_wo = copy.deepcopy(wo)

    # --------------------------------------------------------
    # REMOVE SCENARIO LABELS
    # --------------------------------------------------------

    if "metadata" in agent_wo:

        agent_wo["metadata"].pop(
            "scenario_id",
            None,
        )

        agent_wo["metadata"].pop(
            "scenario_family",
            None,
        )

    # --------------------------------------------------------
    # REMOVE GROUND TRUTH
    # --------------------------------------------------------

    agent_wo.pop(
        "ground_truth",
        None,
    )

    # --------------------------------------------------------
    # REMOVE PROJECT GROUND TRUTH
    # --------------------------------------------------------

    if "project" in agent_wo:

        agent_wo["project"].pop(
            "classified_type",
            None,
        )

        agent_wo["project"].pop(
            "classification_status",
            None,
        )

    # --------------------------------------------------------
    # REMOVE PRECOMPUTED RESEARCH ANSWERS
    # --------------------------------------------------------

    if "research" in agent_wo:

        agent_wo["research"].pop(
            "discrepancies",
            None,
        )

    # --------------------------------------------------------
    # REMOVE PRECOMPUTED QC ANSWERS
    # --------------------------------------------------------

    if "qc" in agent_wo:

        agent_wo["qc"].pop(
            "status",
            None,
        )

        agent_wo["qc"].pop(
            "btp_reasons",
            None,
        )

        agent_wo["qc"].pop(
            "correction_history",
            None,
        )

    return agent_wo


def create_ground_truth(wo):
    """
    Creates evaluator-only expected results.

    Must never be supplied to Foundry specialist agents.
    """

    return {
        "metadata": {
            "synthetic":
                True,

            "dataset_version":
                DATASET_VERSION,

            "wo_id":
                wo["metadata"]["wo_id"],

            "scenario_id":
                wo["metadata"]["scenario_id"],

            "scenario_family":
                wo["metadata"]["scenario_family"],
        },

        "expected":
            copy.deepcopy(
                wo["ground_truth"]
            ),

        "expected_research": {
            "status":
                wo["research"]["status"],

            "discrepancies":
                copy.deepcopy(
                    wo["research"]["discrepancies"]
                ),
        },

        "expected_qc": {
            "status":
                wo["qc"]["status"],

            "btp_reasons":
                copy.deepcopy(
                    wo["qc"]["btp_reasons"]
                ),

            "correction_history":
                copy.deepcopy(
                    wo["qc"]["correction_history"]
                ),
        },
    }


# ============================================================
# DATASET GENERATOR
# ============================================================

def generate_dataset():

    work_orders = []

    index = 1

    # Preserve the 120 v2.1 cases.
    for scenario_name, project_type in SCENARIOS:

        for _ in range(5):

            work_orders.append(
                generate_work_order(
                    index,
                    scenario_name,
                    project_type,
                )
            )

            index += 1

    # Add 20 intake scenario families × 5 variants = 100.
    for scenario_name, project_type in ADDITIONAL_SCENARIOS:
        for _ in range(5):
            work_orders.append(
                generate_work_order(index, scenario_name, project_type)
            )
            index += 1

    assert len(work_orders) == TOTAL_WOS

    return work_orders


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset(work_orders):

    wo_ids = [
        wo["metadata"]["wo_id"]
        for wo in work_orders
    ]

    assert len(work_orders) == TOTAL_WOS

    assert len(set(wo_ids)) == TOTAL_WOS

    assert all(
        wo["metadata"]["synthetic"] is True
        for wo in work_orders
    )

    assert all(
        wo["metadata"]["dataset_version"]
        == DATASET_VERSION
        for wo in work_orders
    )

    assert all(
        wo["metadata"]["wo_id"].startswith(
            "SYN-WO-"
        )
        for wo in work_orders
    )

    # --------------------------------------------------------
    # V2.1 REGRESSION TEST:
    # QC_EVIDENCE_MISMATCH MUST BE VISIBLE
    # --------------------------------------------------------

    mismatch_wos = [
        wo
        for wo in work_orders
        if (
            wo["metadata"]["scenario_family"]
            == "QC_EVIDENCE_MISMATCH"
        )
    ]

    assert len(mismatch_wos) == 5

    for wo in mismatch_wos:

        noc = next(
            item
            for item in wo["evidence"]
            if item["type"] == "NOC"
        )

        permit = next(
            item
            for item in wo["evidence"]
            if item["type"] == "PERMIT"
        )

        noc_gc = (
            noc["extracted_facts"]
            ["general_contractor"]
            ["name"]
        )

        permit_gc = (
            permit["extracted_facts"]
            ["contractor"]
            ["name"]
        )

        assert noc_gc != permit_gc

        assert (
            "EVIDENCE_MISMATCH"
            in wo["qc"]["btp_reasons"]
        )

    # --------------------------------------------------------
    # V2.1 REGRESSION TEST:
    # QC_BTP_CORRECTION MUST BE VISIBLE
    # --------------------------------------------------------

    correction_wos = [
        wo
        for wo in work_orders
        if (
            wo["metadata"]["scenario_family"]
            == "QC_BTP_CORRECTION"
        )
    ]

    assert len(correction_wos) == 5

    for wo in correction_wos:

        customer_gc = (
            wo["customer_input"]
            ["customer_customer"]
            ["name"]
        )

        noc = next(
            item
            for item in wo["evidence"]
            if item["type"] == "NOC"
        )

        permit = next(
            item
            for item in wo["evidence"]
            if item["type"] == "PERMIT"
        )

        noc_gc = (
            noc["extracted_facts"]
            ["general_contractor"]
            ["name"]
        )

        permit_gc = (
            permit["extracted_facts"]
            ["contractor"]
            ["name"]
        )

        # Customer contains the deliberate correction defect.
        assert customer_gc != noc_gc

        # Independent documentary sources agree.
        assert noc_gc == permit_gc

        assert (
            "CUSTOMER_DATA_MISMATCH"
            in wo["qc"]["btp_reasons"]
        )

    return True


# ============================================================
# MANIFEST
# ============================================================

def create_manifest(work_orders):

    project_counts = Counter(
        wo["project"]["classified_type"]
        for wo in work_orders
    )

    source_counts = Counter(
        wo["customer_input"]["source_type"]
        for wo in work_orders
    )

    qc_counts = Counter(
        wo["qc"]["status"]
        for wo in work_orders
    )

    research_counts = Counter(
        wo["research"]["status"]
        for wo in work_orders
    )

    scenario_counts = Counter(
        wo["metadata"]["scenario_family"]
        for wo in work_orders
    )

    return {
        "synthetic":
            True,

        "dataset_version":
            DATASET_VERSION,

        "generator_seed":
            SEED,

        "total_work_orders":
            len(work_orders),

        "project_type_distribution":
            dict(project_counts),

        "entry_source_distribution":
            dict(source_counts),

        "research_status_distribution":
            dict(research_counts),

        "qc_distribution":
            dict(qc_counts),

        "scenario_distribution":
            dict(scenario_counts),
    }


# ============================================================
# S3 HELPERS
# ============================================================

def put_json(
    key,
    value,
):

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(
            value,
            indent=2,
        ),
        ContentType="application/json",
    )


def put_jsonl(
    key,
    records,
):

    body = "\n".join(
        json.dumps(item)
        for item in records
    )

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=body,
        ContentType="application/x-ndjson",
    )


# ============================================================
# LAMBDA HANDLER
# ============================================================

def lambda_handler(event, context):

    # --------------------------------------------------------
    # 1. Generate canonical synthetic records
    # --------------------------------------------------------

    work_orders = generate_dataset()

    # --------------------------------------------------------
    # 2. Validate BEFORE anything is uploaded
    # --------------------------------------------------------

    validate_dataset(
        work_orders
    )

    manifest = create_manifest(
        work_orders
    )

    # --------------------------------------------------------
    # 3. Create isolated agent/evaluator views
    # --------------------------------------------------------

    agent_inputs = []

    ground_truth_records = []

    for wo in work_orders:

        agent_inputs.append(
            create_agent_input(
                wo
            )
        )

        ground_truth_records.append(
            create_ground_truth(
                wo
            )
        )

    # ========================================================
    # AGENT INPUT V2.1
    # ========================================================

    agent_prefix = (
        f"agent-input/"
        f"{DATASET_PATH_VERSION}"
    )

    truth_prefix = (
        f"ground-truth/"
        f"{DATASET_PATH_VERSION}"
    )

    manifest_prefix = (
        f"manifests/"
        f"{DATASET_PATH_VERSION}"
    )

    # --------------------------------------------------------
    # Combined agent JSON
    # --------------------------------------------------------

    put_json(
        key=(
            f"{agent_prefix}/"
            f"work-orders.json"
        ),
        value=agent_inputs,
    )

    # --------------------------------------------------------
    # Combined agent JSONL
    # --------------------------------------------------------

    put_jsonl(
        key=(
            f"{agent_prefix}/"
            f"work-orders.jsonl"
        ),
        records=agent_inputs,
    )

    # --------------------------------------------------------
    # Individual agent Work Orders
    # --------------------------------------------------------

    for wo in agent_inputs:

        wo_id = (
            wo["metadata"]["wo_id"]
        )

        put_json(
            key=(
                f"{agent_prefix}/"
                f"work-orders/"
                f"{wo_id}.json"
            ),
            value=wo,
        )

    # ========================================================
    # EVALUATOR-ONLY GROUND TRUTH V2.1
    # ========================================================

    for truth in ground_truth_records:

        wo_id = (
            truth["metadata"]["wo_id"]
        )

        put_json(
            key=(
                f"{truth_prefix}/"
                f"{wo_id}.expected.json"
            ),
            value=truth,
        )

    # --------------------------------------------------------
    # Combined ground truth JSONL
    # --------------------------------------------------------

    put_jsonl(
        key=(
            f"{truth_prefix}/"
            f"ground-truth.jsonl"
        ),
        records=ground_truth_records,
    )

    # ========================================================
    # MANIFEST V2.1
    # ========================================================

    manifest["architecture"] = {
        "agent_input_prefix":
            f"{agent_prefix}/",

        "ground_truth_prefix":
            f"{truth_prefix}/",

        "ground_truth_exposed_to_agent":
            False,

        "previous_dataset":
            "v2",

        "previous_dataset_modified":
            False,

        "v2_1_changes": [
            (
                "QC_EVIDENCE_MISMATCH now contains "
                "agent-visible documentary conflict"
            ),
            (
                "QC_BTP_CORRECTION now contains "
                "agent-visible customer-data mismatch"
            ),
            (
                "Regression validation prevents "
                "invisible QC defects"
            ),
        ],
    }

    put_json(
        key=(
            f"{manifest_prefix}/"
            f"manifest.json"
        ),
        value=manifest,
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "statusCode":
            200,

        "message":
            (
                f"Synthetic WO Dataset {DATASET_VERSION} "
                "generated successfully"
            ),

        "total_work_orders":
            len(work_orders),

        "agent_input_records":
            len(agent_inputs),

        "ground_truth_records":
            len(ground_truth_records),

        "dataset_version":
            DATASET_VERSION,

        "dataset_path_version":
            DATASET_PATH_VERSION,

        "agent_input_prefix":
            f"{agent_prefix}/",

        "ground_truth_prefix":
            f"{truth_prefix}/",

        "ground_truth_exposed_to_agent":
            False,

        "frozen_v2_modified":
            False,

        "bucket":
            BUCKET_NAME,
    }
