# Autonomous Work Order Intelligence & Operations Platform

> Evidence-aware multi-agent reasoning with deterministic operational control, provenance, quality control, correction workflows, and human review.

## Overview

The **Autonomous Work Order Intelligence & Operations Platform** is a production-oriented AI engineering system designed for construction payment-protection operations.

The platform demonstrates how specialized AI agents can research, reconcile, explain, and evaluate work-order information while deterministic application logic retains control over consequential workflow decisions.

The system combines:

- Multi-agent AI orchestration
- Evidence provenance
- Participant and contractual-chain reasoning
- Discrepancy detection
- Deterministic workflow routing
- Quality-control gates
- Evidence-supported correction overlays
- Human-in-the-loop escalation
- Synthetic evaluation
- Production APIs
- Interactive operations UI
- Cross-cloud architecture
- CI/CD deployment

The core engineering principle is:

> **LLMs reason, extract, explain, and recommend. Deterministic software controls consequential workflow transitions.**

This project uses **synthetic demonstration data only**.

---

## Business Problem

Construction payment-protection workflows depend on information gathered from multiple sources.

A work order may begin with customer-supplied information while research produces additional evidence from sources such as:

- Property records
- Notices of Commencement
- Permits
- Payment bonds
- Supporting public information
- Direct confirmations
- Customer authorizations

These sources may:

- agree
- disagree
- contain missing information
- contain spelling or identity variations
- remain unverified

A conventional LLM workflow introduces risk if it silently changes customer data, invents missing facts, treats unverified information as incorrect, arbitrarily chooses between conflicting documents, or directly controls consequential operational states.

This platform addresses those risks through explicit provenance, deterministic routing, immutable source values, correction overlays, QC gates, and human-review escalation.

---

## System Architecture

```text
                     SYNTHETIC WORK ORDERS
                              │
                              ▼
                         Amazon S3
                              │
                              ▼
                    AWS Retrieval Lambda
                              │
                              ▼
                      API Gateway API
                              │
                              ▼
                         MCP Adapter
                              │
                              ▼
                    Microsoft Foundry
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
          ▼                   ▼                    ▼
       Intake              Research             Evidence
          │                   │                    │
          └───────────────────┼────────────────────┘
                              ▼
                        Discrepancy Agent
                              │
                              ▼
                           QC Agent
                              │
                  ┌───────────┼────────────┐
                  │           │            │
                  ▼           ▼            ▼
               PASS          BTP       HUMAN REVIEW
                  │           │
                  │           ▼
                  │    Research Correction
                  │           │
                  │           ▼
                  │      QC Re-review
                  │           │
                  └───────────┤
                              ▼
                    Deterministic Python
                       Control Plane
                              │
                              ▼
                         FastAPI API
                              │
                              ▼
                      Next.js Console
                              │
                              ▼
                    Azure Container Apps
```

The AI-agent layer does **not** own the final workflow state machine.

Structured agent outputs are validated and passed into deterministic Python routing logic.

---

# Architecture Principles

## 1. Evidence Provenance

Every important fact retains information about where it came from.

The system models the fact lifecycle as:

```text
Customer Claim
      │
      ▼
  Unverified
      │
      ▼
Research Evidence
      │
      ├── MATCH
      ├── MISSING
      └── CONFLICT
      │
      ▼
   Resolution
      │
      ▼
      QC
```

Customer-supplied information is not silently converted into researched truth.

---

## 2. Customer Input vs Resolved Information

Customer input remains logically separate from researched or resolved information.

This distinction prevents the system from accidentally treating a customer claim as independently verified evidence.

The canonical data model includes:

```json
{
  "metadata": {},
  "customer_input": {},
  "project": {},
  "work_details": {},
  "participants": [],
  "contractual_chain": [],
  "evidence": [],
  "communications": [],
  "customer_approvals": [],
  "research": {},
  "qc": {},
  "ground_truth": {}
}
```

`ground_truth` exists only for evaluation.

It is not normal agent evidence.

---

## 3. Immutable Source Records

Original source values remain unchanged.

When the system identifies a correctable mismatch, it creates a separate correction proposal.

```text
Original Source
      │
      ├─────────────────────┐
      │                     │
      ▼                     ▼
Immutable Value      Proposed Correction
                            │
                            ▼
                    Independent QC
                            │
                            ▼
                    Accepted Overlay
```

This provides an auditable distinction between:

- what the source originally said
- what the AI proposed
- what QC verified
- what deterministic logic accepted

---

## 4. Deterministic Control Plane

LLMs do not directly determine consequential workflow transitions.

Python owns:

- workflow routing
- correction limits
- human-review escalation
- correction acceptance
- terminal recommendations
- MCP approval controls

Representative state flow:

```text
STARTED
   │
   ▼
INTAKE
   │
   ▼
RESEARCH
   │
   ▼
EVIDENCE
   │
   ▼
DISCREPANCY
   │
   ▼
QC
   │
   ├── PASS ───────────────► COMPLETE_RECOMMENDED
   │
   ├── BTP ─► RESEARCH_CORRECTION ─► QC_REVIEW
   │
   └── HUMAN_REVIEW ───────► HUMAN_REVIEW
```

A `PASS` represents an intelligence workflow recommendation.

It does not independently perform an external legal or operational action.

---

# Multi-Agent Architecture

The system uses specialized agents instead of one unrestricted general-purpose agent.

| Agent | Responsibility | Tools |
|---|---|---|
| Orchestrator | Coordinates specialist execution | None |
| Intake | Interprets synthetic work-order input | MCP |
| Research | Investigates unresolved information | MCP + Web Search |
| Evidence | Constructs evidence/provenance view | MCP |
| Discrepancy | Identifies matches, conflicts, missing and unverified facts | MCP |
| QC | Performs final intelligence quality gate | MCP |

The orchestrator intentionally has no external tools.

This reduces unnecessary tool authority at the coordination layer.

---

# Evidence Model

The platform models several generic evidence channels.

## Documentary Evidence

Examples include:

- Property records
- Notice of Commencement records
- Permits
- Payment bonds

## Supporting Evidence

Examples include:

- Public web information
- Map/location references

## Direct Confirmation

Information obtained through an explicit confirmation process.

## Customer Authorization

Operational authorization supplied by a customer where the applicable process allows it.

The system does not invent a universal legal ranking between evidence types.

---

# Discrepancy Intelligence

The discrepancy layer distinguishes between:

```text
MATCH
CONFLICT
MISSING
UNVERIFIED
```

A critical semantic rule is:

> **Unverified does not mean incorrect.**

Missing or unverified information alone does not automatically require human review.

Escalation depends on whether the unresolved information is materially required by the established workflow.

---

## Customer Claim vs Documentary Evidence

If a customer-supplied participant value differs from multiple consistent documentary sources, the system may identify a correctable customer-data mismatch.

This can proceed through controlled correction rather than automatically requiring human review.

---

## Documentary Evidence vs Documentary Evidence

If material documentary sources disagree and the system cannot safely determine the correct value, the workflow escalates to:

```text
HUMAN_REVIEW
```

The system does not arbitrarily choose one document.

---

# Quality Control

QC produces one of three primary outcomes:

```text
PASS
BTP
HUMAN_REVIEW
```

`BTP` represents a controlled correction path.

Supported correction categories include:

```text
MISSING_PARTICIPANT
EVIDENCE_MISMATCH
MISSING_CONFIRMATION
DATA_SPELLING_ERROR
PROCESS_FAILURE
CUSTOMER_DATA_MISMATCH
```

Corrections remain separate from immutable source information.

---

# Bounded Correction Workflow

Correction attempts are limited by deterministic application logic.

```text
QC
 │
 ├── PASS
 │
 ├── HUMAN_REVIEW
 │
 └── BTP
       │
       ▼
Research Correction
       │
       ▼
Correction Overlay
       │
       ▼
QC Re-review
       │
       ├── PASS
       ├── HUMAN_REVIEW
       └── Retry within limit
```

Repeated unresolved corrections do not create an infinite autonomous loop.

Once the configured correction limit is exceeded, the workflow escalates to human review.

---

# Tool Governance

The current MCP integration exposes the read-only synthetic operation:

```text
get_work_order
```

Automatic MCP approval is restricted to the explicit allowlist for this read-only operation.

Future write operations or consequential tools must **not** automatically inherit this policy.

---

# Synthetic Evaluation Dataset

The evaluation corpus contains:

```text
120 synthetic work orders
24 scenario families
5 work orders per family
Seed: 42
```

All work orders are synthetic.

The current dataset version is:

```text
v2.1
```

The earlier `v2` dataset remains frozen.

`v2.1` corrected representation defects without rewriting the frozen version.

---

# Production Demonstration Scenarios

The frontend exposes three synthetic golden-path scenarios.

---

## SYN-WO-000001 — Clean Path

### Purpose

Demonstrates autonomous processing when no material evidence conflict requires correction or human intervention.

### Expected Journey

```text
Intake
  ↓
Research
  ↓
Evidence
  ↓
Discrepancy
  ↓
QC
  ↓
Complete Recommended
```

### Safety Behavior

Customer claims remain separate from researched evidence.

Unverified information alone does not create:

- failure
- BTP
- human review

### Expected Outcome

```text
COMPLETE_RECOMMENDED
Human Review: NO
Corrections: 0
```

---

## SYN-WO-000116 — Controlled Correction

### Purpose

Demonstrates an evidence-supported correction when customer participant information differs from consistent documentary evidence.

### Expected Journey

```text
Intake
  ↓
Research
  ↓
Evidence
  ↓
Discrepancy
  ↓
BTP
  ↓
Research Correction
  ↓
QC Re-review
  ↓
Complete Recommended
```

### Safety Behavior

The system:

- preserves the original customer claim
- creates an evidence-supported correction proposal
- stores the correction separately
- requires independent QC verification
- lets deterministic Python control acceptance

### Expected Outcome

```text
COMPLETE_RECOMMENDED
Human Review: NO
Corrections: >= 1
```

---

## SYN-WO-000111 — Human Review

### Purpose

Demonstrates safe escalation when documentary evidence contains an unresolved material disagreement.

### Expected Journey

```text
Intake
  ↓
Research
  ↓
Evidence
  ↓
Discrepancy
  ↓
QC
  ↓
Human Review
```

### Safety Behavior

The system preserves the disagreement rather than:

- arbitrarily selecting one source
- inventing a correction
- silently overwriting evidence

### Expected Outcome

```text
HUMAN_REVIEW
Human Review: YES
Corrections: 0
```

---

# Evaluation Results

A corrected evaluation dataset is maintained separately from earlier mislabeled examples.

Recorded intake-agent baseline:

| Metric | Result |
|---|---:|
| Overall | 154 / 156 |
| Approximate score | 99% |
| Tool selection | 100% |
| Tool call success | 100% |
| Tool call accuracy | 100% |
| Tool output utilization | 83% |
| Latency P50 | 15.1 s |
| Latency P95 | 18.8 s |

Evaluation defects discovered during development were corrected rather than hidden.

Earlier evaluation data contained mislabeled scenario identifiers for several cases. Those labels were corrected in the subsequent evaluation version.

---

# Production API

The backend is implemented with FastAPI.

## Health Check

```http
GET /health
```

## Demo Scenarios

```http
GET /api/v1/demo-scenarios
```

## Start Workflow

```http
POST /api/v1/workflows/{wo_id}/run
```

A successful request returns:

```text
HTTP 202 Accepted
```

with an execution identifier.

## Execution Status

```http
GET /api/v1/executions/{execution_id}
```

The frontend polls this endpoint until the workflow reaches a terminal state.

---

# API Safety Boundary

Demo work-order IDs must match:

```text
^SYN-WO-\d{6}$
```

The public demonstration is restricted to synthetic work orders.

Production CORS is configured using explicit frontend origins rather than a wildcard policy.

---

# Backend Structure

```text
wo-agent-orchestrator/
├── agent_models.py
├── correction_overlay.py
├── observability.py
├── orchestrator.py
├── result_parser.py
├── router.py
├── workflow_state.py
│
├── api/
│   ├── __init__.py
│   ├── execution_store.py
│   ├── main.py
│   ├── schemas.py
│   └── service.py
│
├── tests/
│   ├── test_api.py
│   ├── test_correction_overlay.py
│   ├── test_observability.py
│   ├── test_result_parser.py
│   └── test_router.py
│
├── frontend/
├── Dockerfile
└── requirements.txt
```

Additional specialist regression tests validate individual agent and routing behavior.

---

# Frontend

The operations console is implemented with:

```text
Next.js 16
React 19
TypeScript
Tailwind CSS
Motion
Lucide React
```

The UI provides:

- Synthetic scenario selection
- Scenario Intelligence explanations
- Expected agent journey
- Safety behavior
- Expected outcome
- Workflow execution graph
- QC outcome
- Human-review state
- Correction count
- Evidence metrics
- Discrepancy metrics
- Evidence provenance
- Correction intelligence
- Execution telemetry

The interface follows the visual language of the associated AI engineering portfolio using a dark system UI with blue-to-violet brand accents.

Operational states retain independent semantic colors so branding does not obscure system meaning.

---

# Cross-Cloud Architecture

The project intentionally integrates AWS and Azure services.

## AWS Retrieval Layer

```text
Synthetic Dataset
       │
       ▼
    Amazon S3
       │
       ▼
   AWS Lambda
       │
       ▼
  API Gateway
       │
       ▼
   MCP Adapter
```

AWS provides the synthetic work-order retrieval layer.

---

## Microsoft Foundry

Microsoft Foundry hosts the specialist AI agents and model execution.

The deployed agent system uses:

```text
GPT-5-mini
```

Specialist agents perform intake, research, evidence analysis, discrepancy classification, and QC.

---

## Azure Application Layer

```text
GitHub
   │
   ▼
GitHub Actions
   │
   ▼
Azure Container Registry
   │
   ├──────────────┐
   │              │
   ▼              ▼
Backend Image   Frontend Image
   │              │
   └──────┬───────┘
          ▼
 Azure Container Apps
```

Both frontend and backend are deployed as containers.

---

# CI/CD

GitHub Actions builds and deploys the application containers.

The deployment architecture uses Azure federated identity/OIDC rather than storing a long-lived Azure deployment secret in GitHub.

Separate workflows handle backend and frontend deployment.

Container images are published to Azure Container Registry and deployed to Azure Container Apps.

---

# Execution Store

The current demonstration uses an in-memory, thread-safe execution store.

This creates several intentional limitations:

- execution state does not survive container restart
- execution state is not shared between replicas
- horizontal scaling requires a durable shared state store

The backend therefore runs with a single replica for this version.

A future production architecture should use a durable persistence layer such as a database or distributed state service.

---

# Observability

The orchestration layer emits privacy-safe structured operational telemetry.

Observability avoids logging:

- full work-order payloads
- raw customer information
- complete agent messages

The objective is to capture enough metadata to understand workflow execution without unnecessarily exposing underlying information.

---

# Testing

Run the core automated test suite from the project root:

```bash
python -m pytest tests/ -q
```

Verified core test result:

```text
75 passed
```

Frontend validation:

```bash
cd frontend
npm run lint
npm run build
```

Both linting and optimized production builds are required before deployment.

---

# Privacy & Data Boundary

This repository uses **synthetic data only**.

The following must never be placed in this repository, demonstration environment, evaluation corpus, prompts, vector stores, screenshots, or portfolio artifacts:

- Real customer names
- Real work-order identifiers
- Real project addresses
- Real customer documents
- Real project records
- Confidential attachments
- Proprietary customer datasets
- Other identifying production information

Real operational information is not part of the implementation dataset.

The project models the generic business workflow using synthetic scenarios.

---

# Security Controls

The system demonstrates several explicit controls:

- Synthetic-only public demonstration
- Read-only MCP allowlist
- No automatic approval inheritance for future consequential tools
- Deterministic workflow routing
- Explicit human-review escalation
- Immutable source records
- Controlled correction overlays
- Bounded correction attempts
- Privacy-safe telemetry
- Azure OIDC deployment
- Explicit production CORS origins

The current public AWS retrieval endpoint exists only for the synthetic demonstration architecture and should be hardened before adapting the pattern to non-public information.

---

# Known Limitations

This is a portfolio-grade production demonstration, not a deployed legal decision system.

Current limitations include:

1. Execution state is stored in memory.
2. Backend scaling is intentionally limited to one replica.
3. Public demonstration supports synthetic work orders only.
4. The synthetic AWS retrieval endpoint requires stronger authentication before any non-public use.
5. AI outputs remain probabilistic.
6. External web research can vary over time.
7. Human review remains necessary for unresolved material evidence conflicts.
8. Legal requirements are not invented by the system.
9. The platform does not independently send notices or perform consequential external actions.
10. Production adoption would require organization-specific security, legal, compliance, monitoring, governance, and operational controls.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Languages | Python, TypeScript |
| AI Platform | Microsoft Foundry |
| Model | GPT-5-mini |
| Agent Tools | MCP, Web Search |
| Backend API | FastAPI |
| Testing | pytest |
| Frontend | Next.js 16 |
| UI | React 19 |
| Styling | Tailwind CSS + custom CSS |
| Motion | Motion |
| Icons | Lucide React |
| AWS Storage | Amazon S3 |
| AWS Compute | AWS Lambda |
| AWS API | API Gateway |
| Container Registry | Azure Container Registry |
| Runtime | Azure Container Apps |
| CI/CD | GitHub Actions |
| Deployment Authentication | Azure federated identity / OIDC |

---

# Engineering Concepts Demonstrated

This project goes beyond simply connecting multiple LLM agents.

It demonstrates the separation between:

```text
Probabilistic Intelligence
          │
          ▼
Structured Interpretation
          │
          ▼
Deterministic Control
          │
          ▼
Operational Decision
```

Engineering concepts demonstrated include:

- Multi-agent decomposition
- Agent specialization
- MCP tool integration
- Tool governance
- Structured LLM-output parsing
- Evidence provenance
- Participant reasoning
- Discrepancy classification
- Deterministic state routing
- Immutable-source architecture
- Correction overlays
- Bounded autonomous correction
- Human-in-the-loop escalation
- Synthetic evaluation
- Regression testing
- Failure-case testing
- FastAPI production APIs
- Next.js application engineering
- Docker containerization
- Cross-cloud integration
- CI/CD
- Federated deployment identity
- Privacy-aware observability
- Production UI engineering

---

# Design Philosophy

The architecture deliberately separates responsibilities:

### AI Layer

Responsible for:

- extraction
- research
- reasoning
- discrepancy explanation
- recommendations

### Deterministic Application Layer

Responsible for:

- validating structured outputs
- enforcing workflow rules
- correction limits
- routing
- acceptance of correction overlays
- human-review escalation
- terminal workflow recommendations

### Human Layer

Responsible for:

- unresolved material conflicts
- exceptional cases
- consequential review where automation cannot safely resolve the evidence

This creates a controlled architecture:

```text
AI proposes
     ↓
Software validates
     ↓
Rules control
     ↓
Humans review exceptions
```

---

# Project Status

| Area | Status |
|---|---|
| Synthetic dataset | Complete |
| AWS retrieval layer | Complete |
| MCP integration | Complete |
| Foundry specialist agents | Complete |
| Deterministic orchestration | Complete |
| Discrepancy engine | Complete |
| QC engine | Complete |
| Correction workflow | Complete |
| Human-review routing | Complete |
| Evaluation | Complete |
| Automated tests | Passing |
| FastAPI backend | Complete |
| Next.js frontend | Complete |
| Azure backend deployment | Complete |
| Azure frontend deployment | Complete |
| GitHub Actions CI/CD | Complete |
| Production scenario validation | Complete |
| Frontend production acceptance | Complete |

---

# Repository

This project is part of:

**Construction Legal AI Suite**

GitHub:

`gopalgk53/construction-legal-ai-suite`

Project directory:

```text
wo-agent-orchestrator/
```

Portfolio:

`gopalakrishnagenai.in`

---

# Disclaimer

This project demonstrates AI and software-engineering architecture for construction payment-protection workflows.

It is not legal advice and should not be treated as a substitute for qualified legal, compliance, or operational review.

Consequential production decisions should remain subject to appropriate deterministic controls, organizational policies, and human oversight.