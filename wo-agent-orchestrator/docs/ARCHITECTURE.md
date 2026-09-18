# System Architecture

## Autonomous Work Order Intelligence & Operations Platform

This document describes the production architecture, control boundaries, agent responsibilities, evidence model, safety mechanisms, cloud topology, and execution lifecycle of the Autonomous Work Order Intelligence & Operations Platform.

---

## 1. Architecture Objective

The platform is designed around one fundamental separation:

```text
Probabilistic AI
      │
      ▼
Structured Results
      │
      ▼
Deterministic Control
      │
      ▼
Operational Recommendation
```

AI agents provide intelligence.

Application code retains authority over workflow transitions.

This prevents probabilistic model output from directly controlling consequential operational states.

---

## 2. End-to-End Architecture

```mermaid
flowchart TB
    DATA["Synthetic Work Orders<br/>120 WOs / 24 Scenario Families"]
    S3["Amazon S3<br/>Versioned Synthetic Dataset"]
    RET["AWS Lambda<br/>Retrieval Service"]
    APIGW["Amazon API Gateway<br/>Synthetic Retrieval API"]
    MCP["AWS Lambda MCP Adapter<br/>get_work_order"]

    subgraph FOUNDRY["Microsoft Foundry — AI Intelligence Layer"]
        INTAKE["Intake Agent"]
        RESEARCH["Research Agent"]
        EVIDENCE["Evidence Agent"]
        DISC["Discrepancy Agent"]
        QC["QC Agent"]
        RC["Research Correction"]
    end

    CONTROL["Python Deterministic<br/>Control Plane"]
    PARSER["Structured Result Parser"]
    ROUTER["Deterministic Router"]
    OVERLAY["Correction Overlay"]
    STATE["Workflow State"]
    API["FastAPI<br/>Execution API"]
    STORE["Thread-Safe<br/>In-Memory Execution Store"]
    UI["Next.js 16 / React 19<br/>Operations Console"]

    subgraph AZURE["Azure Production Runtime"]
        ACR["Azure Container Registry"]
        BACKEND["Backend<br/>Azure Container App"]
        FRONTEND["Frontend<br/>Azure Container App"]
    end

    GHA["GitHub Actions<br/>OIDC Deployment"]

    DATA --> S3
    S3 --> RET
    RET --> APIGW
    APIGW --> MCP

    MCP --> INTAKE
    MCP --> RESEARCH
    MCP --> EVIDENCE
    MCP --> DISC
    MCP --> QC

    INTAKE --> CONTROL
    RESEARCH --> CONTROL
    EVIDENCE --> CONTROL
    DISC --> CONTROL
    QC --> CONTROL
    RC --> CONTROL

    CONTROL --> PARSER
    PARSER --> ROUTER
    ROUTER --> STATE
    ROUTER --> OVERLAY
    OVERLAY --> RC
    RC --> QC

    API --> CONTROL
    API <--> STORE
    UI --> API

    GHA --> ACR
    ACR --> BACKEND
    ACR --> FRONTEND

    BACKEND --> API
    FRONTEND --> UI
```

---

## 3. Responsibility Boundaries

### AI Layer

Responsible for:

- extraction
- research
- evidence interpretation
- discrepancy reasoning
- explanations
- correction proposals
- QC recommendations

The AI layer does not own final workflow transitions.

### Deterministic Application Layer

Responsible for:

- structured-output validation
- state transitions
- correction attempt limits
- correction-overlay acceptance
- human-review routing
- terminal recommendations
- MCP approval policy

### Human Layer

Responsible for unresolved or exceptional situations that the system cannot safely resolve.

Examples include unresolved material documentary conflicts.

---

## 4. Agent Topology

```mermaid
flowchart LR
    O["Orchestrator<br/>No external tools"]

    I["Intake Agent<br/>MCP"]
    R["Research Agent<br/>MCP + Web Search"]
    E["Evidence Agent<br/>MCP"]
    D["Discrepancy Agent<br/>MCP"]
    Q["QC Agent<br/>MCP"]

    O --> I
    I --> R
    R --> E
    E --> D
    D --> Q
```

The orchestrator intentionally has no external tools.

Specialist agents receive only the tools required for their responsibility.

---

## 5. Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> STARTED

    STARTED --> INTAKE
    INTAKE --> RESEARCH
    RESEARCH --> EVIDENCE
    EVIDENCE --> DISCREPANCY
    DISCREPANCY --> QC

    DISCREPANCY --> HUMAN_REVIEW: unresolved material conflict

    QC --> COMPLETE_RECOMMENDED: PASS
    QC --> RESEARCH_CORRECTION: BTP
    QC --> HUMAN_REVIEW: HUMAN_REVIEW

    RESEARCH_CORRECTION --> QC_REVIEW
    QC_REVIEW --> COMPLETE_RECOMMENDED: verified
    QC_REVIEW --> RESEARCH_CORRECTION: retry within limit
    QC_REVIEW --> HUMAN_REVIEW: unresolved / retry limit

    COMPLETE_RECOMMENDED --> [*]
    HUMAN_REVIEW --> [*]
```

The state machine is controlled by Python rather than model-generated transitions.

---

## 6. Evidence Provenance Architecture

```mermaid
flowchart LR
    CLAIM["Customer Claim"]
    UNVERIFIED["Unverified"]
    EVIDENCE["Research Evidence"]
    MATCH["Match"]
    MISSING["Missing"]
    CONFLICT["Conflict"]
    RESOLUTION["Resolution"]
    QC["QC"]

    CLAIM --> UNVERIFIED
    UNVERIFIED --> EVIDENCE

    EVIDENCE --> MATCH
    EVIDENCE --> MISSING
    EVIDENCE --> CONFLICT

    MATCH --> RESOLUTION
    MISSING --> RESOLUTION
    CONFLICT --> RESOLUTION

    RESOLUTION --> QC
```

A customer claim remains a customer claim unless independently supported.

`UNVERIFIED` is not equivalent to `INCORRECT`.

---

## 7. Correction Architecture

Source values are immutable.

```mermaid
flowchart TB
    ORIGINAL["Original Source Value<br/>Immutable"]
    ISSUE["QC / Evidence Mismatch"]
    PROPOSAL["PROPOSED Correction"]
    VERIFY["Independent QC Verification"]
    ACCEPT["Deterministic Acceptance"]
    EFFECTIVE["Effective Context"]
    HR["Human Review"]

    ORIGINAL --> ISSUE
    ISSUE --> PROPOSAL
    ORIGINAL --> VERIFY
    PROPOSAL --> VERIFY

    VERIFY --> ACCEPT
    VERIFY --> HR

    ACCEPT --> EFFECTIVE
    ORIGINAL --> EFFECTIVE
```

The correction overlay does not rewrite the original evidence.

Instead, an effective view can combine immutable source information with accepted corrections.

---

## 8. Correction Safety

The deterministic layer enforces:

```text
Original data
    ↓
Evidence-supported proposal
    ↓
PROPOSED correction
    ↓
Independent QC
    ↓
Python validation
    ↓
Accepted overlay
```

Correction cycles are bounded.

The system escalates instead of entering an unlimited autonomous correction loop.

---

## 9. Discrepancy Decision Model

```mermaid
flowchart TD
    FACT["Fact / Participant Value"]
    COMPARE["Compare Evidence"]

    MATCH["MATCH"]
    MISS["MISSING"]
    UNVER["UNVERIFIED"]
    CONFLICT["CONFLICT"]

    CUSTOMER["Customer Claim vs<br/>Consistent Documentary Evidence"]
    DOC["Document vs Document<br/>Material Conflict"]

    CORRECT["Controlled Correction Path"]
    CONTINUE["Continue to QC"]
    HUMAN["Human Review"]

    FACT --> COMPARE

    COMPARE --> MATCH
    COMPARE --> MISS
    COMPARE --> UNVER
    COMPARE --> CONFLICT

    MATCH --> CONTINUE
    MISS --> CONTINUE
    UNVER --> CONTINUE

    CONFLICT --> CUSTOMER
    CONFLICT --> DOC

    CUSTOMER --> CORRECT
    DOC --> HUMAN
```

Missing and unverified information do not automatically trigger escalation.

Materiality and established workflow requirements matter.

---

## 10. MCP Tool Boundary

Current automatically approved tool:

```text
sunray-wo-mcp
└── get_work_order
```

Characteristics:

- read-only
- synthetic-data only
- explicitly allowlisted

The approval rule is intentionally narrow.

Future tools capable of mutation or consequential actions must receive separate approval policies.

---

## 11. AWS Retrieval Architecture

```mermaid
flowchart LR
    GEN["Synthetic Generator"]
    S3["Amazon S3"]
    LAMBDA["Retrieval Lambda"]
    GW["API Gateway"]
    MCP["MCP Lambda"]
    FOUNDRY["Foundry Agent"]

    GEN --> S3
    S3 --> LAMBDA
    LAMBDA --> GW
    GW --> MCP
    MCP --> FOUNDRY
```

The retrieval layer exposes synthetic work-order information to the agent system.

The architecture intentionally keeps source data retrieval separate from AI reasoning.

---

## 12. Application Architecture

```mermaid
flowchart LR
    USER["User"]
    WEB["Next.js Operations Console"]
    API["FastAPI"]
    SERVICE["Workflow Service"]
    EXEC["Execution Store"]
    ORCH["Orchestrator"]
    AGENTS["Foundry Agents"]

    USER --> WEB
    WEB -->|POST workflow| API
    API --> SERVICE
    SERVICE --> EXEC
    SERVICE --> ORCH
    ORCH --> AGENTS

    WEB -->|poll execution| API
    API --> EXEC
    EXEC --> API
    API --> WEB
```

Workflow execution is asynchronous from the frontend perspective.

The frontend starts an execution and polls for status.

---

## 13. API Boundary

Supported application endpoints:

```text
GET  /health

GET  /api/v1/demo-scenarios

POST /api/v1/workflows/{wo_id}/run

GET  /api/v1/executions/{execution_id}
```

Synthetic work-order identifiers are validated against:

```regex
^SYN-WO-\d{6}$
```

---

## 14. Execution Store

The current execution store is:

- in-memory
- thread-safe
- intentionally limited to the portfolio demonstration

Because state is local to a container:

```text
Container restart
      ↓
Execution state lost
```

and:

```text
Replica A state ≠ Replica B state
```

Therefore the backend currently operates with one replica.

A production evolution should introduce durable shared state.

Possible future implementations include:

```text
PostgreSQL
Redis
Cosmos DB
Durable workflow/state service
```

The exact choice should depend on production requirements.

---

## 15. Azure Deployment Architecture

```mermaid
flowchart TB
    GH["GitHub Repository"]
    ACTION["GitHub Actions"]
    OIDC["Azure Federated Identity / OIDC"]
    ACR["Azure Container Registry"]

    BACK["Backend Container Image"]
    FRONT["Frontend Container Image"]

    ENV["Azure Container Apps Environment"]

    BAPP["wo-intelligence-api"]
    FAPP["wo-intelligence-web"]

    GH --> ACTION
    ACTION --> OIDC
    OIDC --> ACR

    ACTION --> BACK
    ACTION --> FRONT

    BACK --> ACR
    FRONT --> ACR

    ACR --> BAPP
    ACR --> FAPP

    BAPP --> ENV
    FAPP --> ENV
```

No long-lived Azure deployment secret is required by the GitHub deployment workflow.

---

## 16. Cross-Cloud Boundary

```text
AWS
│
├── Synthetic dataset
├── S3
├── Retrieval Lambda
├── API Gateway
└── MCP adapter
        │
        ▼
Microsoft Foundry
│
├── Model execution
├── Specialist agents
├── MCP access
└── Research tooling
        │
        ▼
Deterministic Python Application
        │
        ▼
Azure
│
├── Container Registry
├── Backend Container App
└── Frontend Container App
```

This architecture demonstrates cross-cloud integration without requiring every system component to run on the same provider.

---

## 17. CI/CD Boundary

The deployment flow is:

```text
Code change
    ↓
Git commit
    ↓
GitHub
    ↓
GitHub Actions
    ↓
OIDC authentication
    ↓
Container build
    ↓
Azure Container Registry
    ↓
Azure Container Apps revision
    ↓
Production traffic
```

Frontend and backend deployment workflows remain independently deployable.

---

## 18. Privacy Boundary

The implementation is synthetic-only.

```text
Real Operational Data
        │
        X
        │
        ▼
Portfolio System
```

The portfolio system must not contain:

- real customer names
- real work-order IDs
- real addresses
- real project documents
- real attachments
- proprietary datasets
- confidential customer information

Synthetic scenarios model workflow behavior without reproducing production information.

---

## 19. Observability Boundary

The observability design favors structured operational metadata.

```text
Workflow
   ↓
Stage / status metadata
   ↓
Structured telemetry
```

It intentionally avoids logging full work-order payloads or raw agent messages.

This reduces unnecessary information exposure.

---

## 20. Human-in-the-Loop Boundary

Human review is a designed system state rather than an AI failure.

```mermaid
flowchart TD
    AI["AI Analysis"]
    SAFE{"Safe deterministic<br/>route available?"}
    AUTO["Continue Workflow"]
    HUMAN["Human Review"]

    AI --> SAFE
    SAFE -->|Yes| AUTO
    SAFE -->|No| HUMAN
```

Examples that can require human review include unresolved material documentary conflicts or repeated failed correction attempts.

---

## 21. Golden Paths

### Clean

```text
SYN-WO-000001

Intake
→ Research
→ Evidence
→ Discrepancy
→ QC
→ Complete Recommended
```

### Controlled Correction

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

### Safety Escalation

```text
SYN-WO-000111

Intake
→ Research
→ Evidence
→ Discrepancy
→ QC
→ Human Review
```

Together these demonstrate:

```text
Autonomy
+
Correction
+
Escalation
```

rather than demonstrating only successful AI execution.

---

## 22. Production Evolution

A larger production implementation would require additional controls before processing non-public operational data.

Examples include:

- durable execution persistence
- stronger API authentication
- private networking
- secret rotation
- centralized authorization
- durable audit history
- expanded telemetry
- distributed tracing
- production alerting
- model/version governance
- prompt/version governance
- dataset governance
- organization-specific compliance review
- legal review of consequential workflows
- load testing
- disaster recovery
- multi-replica execution coordination

These are deliberately identified as future production requirements rather than represented as already implemented.

---

## 23. Architectural Outcome

The final architecture demonstrates a controlled autonomous AI pattern:

```text
Evidence
   ↓
Specialist AI
   ↓
Structured Results
   ↓
Deterministic Validation
   ↓
QC / Correction / Escalation
   ↓
Operational Recommendation
```

The most important property of the system is not the number of agents.

It is the explicit separation between **probabilistic reasoning and deterministic authority**.