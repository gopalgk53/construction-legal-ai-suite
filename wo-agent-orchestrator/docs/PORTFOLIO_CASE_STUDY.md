# Autonomous Work Order Intelligence & Operations Platform

## Portfolio Case Study

### Production-Grade Multi-Agent AI for Construction Payment-Protection Operations

---

## Executive Summary

I designed and built an evidence-aware multi-agent AI platform for construction payment-protection workflows.

The system processes synthetic work orders through specialized AI agents for:

- intake
- research
- evidence analysis
- discrepancy detection
- quality control
- controlled correction

The key architectural challenge was not simply connecting multiple agents.

It was determining:

> **Where should AI autonomy stop, and where should deterministic software take control?**

The final system separates probabilistic AI reasoning from consequential workflow authority.

```text
LLM Intelligence
       ↓
Structured Results
       ↓
Deterministic Python Control
       ↓
QC / Correction / Escalation
       ↓
Operational Recommendation
```

The platform is deployed as a cross-cloud production demonstration using AWS, Microsoft Foundry, FastAPI, Next.js, Docker, GitHub Actions, and Azure Container Apps.

All portfolio and evaluation data is synthetic.

---

# The Problem

Construction payment-protection workflows require information from multiple sources to be reconciled before operational processing can safely continue.

Inputs can include:

```text
Customer-provided information
Property records
Notices of Commencement
Permits
Payment bonds
Supporting public information
Direct confirmations
Customer authorizations
```

These sources do not always agree.

The system therefore needs to distinguish between:

```text
MATCH
CONFLICT
MISSING
UNVERIFIED
```

A naive LLM implementation could introduce serious engineering problems by:

- treating customer claims as verified facts
- interpreting unverified information as incorrect
- silently overwriting source information
- inventing corrections
- arbitrarily resolving documentary conflicts
- looping repeatedly through autonomous correction
- directly controlling consequential workflow states

The architecture was designed specifically to prevent these behaviors.

---

# My Solution

I implemented a specialized multi-agent architecture backed by a deterministic Python control plane.

```text
Synthetic Work Orders
        ↓
AWS Retrieval
        ↓
MCP
        ↓
Microsoft Foundry Agents
        ↓
Structured Parsing
        ↓
Deterministic Router
        ↓
QC / Correction / Human Review
        ↓
FastAPI
        ↓
Next.js Operations Console
        ↓
Azure Container Apps
```

---

# Multi-Agent Design

The intelligence layer uses specialist agents with clearly separated responsibilities.

| Agent | Responsibility |
|---|---|
| Intake | Understand work-order input |
| Research | Investigate unresolved information |
| Evidence | Construct evidence/provenance view |
| Discrepancy | Detect matches, conflicts, missing and unverified facts |
| QC | Perform final intelligence quality review |

The coordinating orchestrator intentionally has no external tools.

Specialists receive only the tools required for their responsibilities.

---

# Evidence Provenance

One of the most important design decisions was separating customer input from independently researched information.

```text
Customer Claim
      ↓
Unverified
      ↓
Research Evidence
      ↓
Match / Missing / Conflict
      ↓
Resolution
      ↓
QC
```

The architecture explicitly establishes:

```text
UNVERIFIED ≠ INCORRECT
```

A customer claim can remain unverified without automatically becoming an error.

This prevents unnecessary correction and human-review escalation.

---

# Deterministic Control Plane

LLMs provide intelligence, but they do not directly control workflow state.

Python owns:

- stage routing
- correction limits
- human-review escalation
- correction acceptance
- terminal recommendations
- tool approval boundaries

This creates a clear authority model:

```text
AI proposes
     ↓
Software validates
     ↓
Rules control
     ↓
Humans handle unresolved exceptions
```

---

# Immutable Correction Architecture

When the system detects a correctable mismatch, it does not modify the original source.

Instead:

```text
Original Value
      ↓
Evidence Mismatch
      ↓
PROPOSED Correction
      ↓
Independent QC
      ↓
Deterministic Acceptance
      ↓
Effective Context
```

The original information remains available for auditability.

---

# Human-in-the-Loop Safety

Human review is not treated as a system failure.

It is an intentional terminal safety path.

For example:

```text
Document A
    │
    X
    │
Document B
    ↓
Unresolved material conflict
    ↓
HUMAN_REVIEW
```

The system does not force an autonomous answer when evidence cannot safely support one.

---

# Synthetic Evaluation

I created a fully synthetic evaluation corpus containing:

```text
120 work orders
24 scenario families
5 work orders per family
Seed: 42
```

This allowed the system to test realistic workflow behavior without exposing customer information.

The dataset is versioned, and corrections were introduced through a new dataset version rather than rewriting the frozen previous version.

---

# Evaluation Results

Recorded intake-agent baseline:

| Metric | Result |
|---|---:|
| Correct evaluations | 154 / 156 |
| Approximate score | 99% |
| Tool selection | 100% |
| Tool call success | 100% |
| Tool call accuracy | 100% |
| Tool output utilization | 83% |
| Latency P50 | 15.1 s |
| Latency P95 | 18.8 s |

Evaluation defects discovered during testing were corrected rather than hidden.

---

# Golden-Path Validation

The deployed system was validated against three materially different synthetic scenarios.

## Straight-Through Autonomy

```text
SYN-WO-000001

Intake
→ Research
→ Evidence
→ Discrepancy
→ QC
→ Complete Recommended
```

Expected:

```text
Human Review: NO
Corrections: 0
```

---

## Controlled Autonomous Correction

```text
SYN-WO-000116

Intake
→ Research
→ Evidence
→ Discrepancy
→ BTP
→ Research Correction
→ QC Re-review
→ Complete Recommended
```

Expected:

```text
Human Review: NO
Corrections: >= 1
```

The original source remains immutable.

---

## Safety Escalation

```text
SYN-WO-000111

Intake
→ Research
→ Evidence
→ Discrepancy
→ QC
→ Human Review
```

Expected:

```text
Human Review: YES
Corrections: 0
```

Together the three scenarios demonstrate:

```text
AUTONOMY
+
CORRECTION
+
ESCALATION
```

---

# Production API

I exposed the orchestration system through FastAPI.

```text
GET  /health

GET  /api/v1/demo-scenarios

POST /api/v1/workflows/{wo_id}/run

GET  /api/v1/executions/{execution_id}
```

Workflow execution follows an asynchronous API pattern:

```text
POST workflow
      ↓
202 Accepted
      ↓
execution_id
      ↓
Frontend polling
      ↓
Terminal result
```

---

# Operations Console

I built a production frontend using:

```text
Next.js 16
React 19
TypeScript
Tailwind CSS
Motion
Lucide React
```

The interface visualizes:

- scenario purpose
- agent journey
- workflow stages
- expected safety behavior
- terminal outcome
- evidence metrics
- discrepancy metrics
- QC status
- correction count
- human-review state
- evidence provenance
- correction intelligence

The UI is designed as an AI operations console rather than a generic dashboard.

---

# Cross-Cloud Architecture

The project integrates multiple cloud platforms intentionally.

## AWS

Used for the synthetic retrieval layer:

```text
Amazon S3
AWS Lambda
API Gateway
MCP Adapter
```

## Microsoft Foundry

Used for:

```text
GPT-5-mini
Specialist agents
MCP integration
Research tooling
```

## Azure

Used for:

```text
Azure Container Registry
Azure Container Apps
Production backend
Production frontend
```

---

# CI/CD

GitHub Actions builds and deploys the application.

Deployment authentication uses:

```text
GitHub
   ↓
OIDC federation
   ↓
Azure
```

rather than relying on a long-lived Azure deployment secret.

Frontend and backend deployment pipelines remain independently deployable.

---

# Testing

Core automated test suite:

```text
75 passed
```

The test strategy covers:

- structured parsing
- deterministic routing
- correction overlays
- observability
- API behavior

Frontend validation includes linting and optimized production builds.

---

# Privacy Engineering

The project maintains a strict synthetic-data boundary.

Real customer information is excluded from:

```text
GitHub
AWS demonstration data
Microsoft Foundry prompts/datasets
Azure application data
Evaluation datasets
Portfolio screenshots
```

The project demonstrates the operational pattern without reproducing proprietary production information.

---

# Production Limitation I Chose to Document

The current API uses an in-memory execution store.

This means execution state does not survive container restart and cannot safely support independent state across multiple replicas.

Rather than hiding this limitation, the backend is intentionally constrained to one replica.

A scaled production implementation would introduce durable shared execution state before horizontal scaling.

This demonstrates an important engineering principle:

> Production maturity includes knowing what a system cannot safely do yet.

---

# Technology Stack

```text
Python
FastAPI
pytest
Microsoft Foundry
GPT-5-mini
MCP
AWS S3
AWS Lambda
Amazon API Gateway
Next.js
React
TypeScript
Tailwind CSS
Motion
Docker
Azure Container Registry
Azure Container Apps
GitHub Actions
OIDC
```

---

# Key Engineering Outcomes

The project demonstrates practical experience with:

- Multi-agent architecture
- LLM application engineering
- MCP integration
- Tool governance
- Structured output validation
- Evidence provenance
- Deterministic state machines
- AI safety boundaries
- Human-in-the-loop systems
- Autonomous correction
- Evaluation engineering
- Synthetic data generation
- FastAPI
- Async API patterns
- React/Next.js
- Docker
- AWS
- Azure
- CI/CD
- OIDC
- Production deployment
- Observability
- Privacy-aware AI architecture

---

# What Makes This Project Different

The differentiator is not simply that the project uses multiple AI agents.

The system was designed around **controlled autonomy**.

```text
AI is strong where reasoning is useful.

Software is authoritative where deterministic behavior is required.

Humans remain part of the architecture where evidence cannot safely support autonomous resolution.
```

That separation is the central production engineering principle demonstrated by the project.

---

# Resume Bullets

### Option A — Detailed

- Architected and deployed an evidence-aware multi-agent construction payment-protection platform using **Python, Microsoft Foundry, GPT-5-mini, MCP, FastAPI, AWS, Next.js, Docker and Azure Container Apps**, separating probabilistic LLM reasoning from deterministic workflow control.

- Engineered a **deterministic orchestration and QC layer** with evidence provenance, structured output validation, immutable correction overlays, bounded autonomous correction, discrepancy classification and human-in-the-loop escalation for unresolved material conflicts.

- Built a **120-work-order synthetic evaluation corpus across 24 scenario families** and achieved a recorded **154/156 (~99%) intake-agent evaluation baseline**, including 100% tool-selection, tool-call-success and tool-call-accuracy measurements.

- Productionized the system with **FastAPI asynchronous execution APIs, Next.js/React operations UI, Docker, Azure Container Registry, Azure Container Apps and GitHub Actions OIDC-based CI/CD**, validating straight-through, correction and human-review golden paths.

### Option B — Compact

- Built and deployed a production-oriented **multi-agent AI operations platform** using Microsoft Foundry, GPT-5-mini, MCP, FastAPI, AWS and Azure, with deterministic Python routing controlling consequential workflow transitions.

- Implemented **evidence provenance, discrepancy detection, immutable correction overlays, QC gates and human-in-the-loop escalation**, backed by 120 synthetic work orders and a recorded ~99% intake-agent evaluation baseline.

- Productionized the platform with **Next.js, Docker, Azure Container Apps and GitHub Actions OIDC CI/CD**, validating autonomous, controlled-correction and safety-escalation workflows.

---

# Interview Summary

If asked to explain the project in approximately one minute:

> I built an autonomous work-order intelligence platform for construction payment-protection operations. Instead of using one general LLM, I created specialist agents for intake, research, evidence analysis, discrepancy detection and QC using Microsoft Foundry and MCP. The important architectural decision was that the agents do not control consequential workflow states. Their structured outputs are parsed and passed into a deterministic Python state machine that controls correction limits, QC routing and human escalation. I also designed immutable correction overlays so AI corrections never silently rewrite source information. I evaluated the system with 120 synthetic work orders across 24 scenario families, exposed it through FastAPI, built a Next.js operations console, and deployed the system using AWS retrieval services, Azure Container Apps and GitHub Actions with OIDC. The project demonstrates controlled autonomy rather than unrestricted agent behavior.

---

# Final Portfolio Message

**Autonomous Work Order Intelligence & Operations Platform**

A production-oriented, evidence-aware multi-agent AI system demonstrating how LLM reasoning, deterministic software controls, evidence provenance, autonomous correction, QC and human review can be combined into a safer operational AI architecture.