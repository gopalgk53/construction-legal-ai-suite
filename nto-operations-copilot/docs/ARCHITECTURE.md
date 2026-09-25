# Architecture

## Purpose

NTO Operations Copilot is a teaching and exception-guidance interface. It is not an autonomous notice-processing system. The researcher remains responsible for reviewing sources, confirming facts, recording provenance and escalating unresolved material conflicts.

## Components

### Frontend

The Next.js application provides:

- Work-order entry
- A 100-item synthetic request queue grouped into 20 operational scenarios
- A retrieved intake summary with customer claims and supplied references
- Six-stage research navigation
- Current-task instructions and stopping conditions
- Synthetic example situations
- A full-height, independently scrolling research-coach chat
- Query-specific `Answer`, `Why`, and `Next step` presentation
- Loading and connection-error states

The frontend calls the API configured by `NEXT_PUBLIC_NTO_API_BASE_URL`.

### API gateway

The FastAPI service is the security and policy boundary between the browser and Foundry. It:

- Validates request length and shape with Pydantic
- Authenticates with `DefaultAzureCredential`
- Calls one configured Foundry agent
- Approves only the explicitly allowlisted MCP lookup tool
- Limits MCP approval handling to three rounds
- Uses a 90-second timeout per Foundry call
- Keeps the full intake evidence report away from the browser
- Requests a second, concise grounded answer
- Returns stable HTTP errors without exposing internal exception data

### Foundry agent

Current agent reference:

- Name: `wo-intake-agent`
- Version: `3`
- Project endpoint: configured through `AZURE_AI_PROJECT_ENDPOINT`

The agent owns the MCP connection and uses the read-only work-order retrieval tool.

### MCP data source

The gateway will auto-approve only:

```text
server label: sunray-wo-mcp
tool name:    get_work_order
```

Any other MCP approval request fails closed.

## Request lifecycle

1. The researcher enters a WO number.
2. The frontend sends it to `POST /api/work-orders/lookup` and keeps the previous WO active while retrieval runs.
3. The agent retrieves the record through the allowlisted `sunray-wo-mcp.get_work_order` tool.
4. Only a confirmed lookup changes the active WO; a missing or failed lookup remains visible as an error.
5. The researcher asks a question about the confirmed WO.
6. The frontend sends the WO number, question and current step to `POST /api/coach`.
7. The API constructs a process-guidance request for the configured Foundry agent.
8. The agent retrieves the WO evidence and returns an evidence-oriented intake result.
9. The gateway keeps that result server-side and requests a second answer constrained to 90 words.
10. The concise answer is returned and formatted as `Answer`, `Why`, and `Next step`.

## Trust boundaries

| Boundary | Allowed | Not allowed |
|---|---|---|
| Browser to API | WO ID, question, current step | Azure credentials, MCP credentials |
| API to Foundry | Research context and agent reference | Arbitrary client-selected agent names |
| Foundry to MCP | Approved read-only WO lookup | Unapproved tools or mutations |
| Coach response | Guidance grounded in retrieved evidence | Invented facts or silent conflict resolution |

## Authentication

Locally, `DefaultAzureCredential` can use Azure CLI authentication. In Azure, the API App Service uses its system-assigned managed identity. The frontend has no Azure identity and no direct Foundry access.

Required Azure roles for the API managed identity:

- `Foundry Agent Consumer` on the Foundry project
- `Foundry User` on the Foundry project
- `Cognitive Services OpenAI User` on the Foundry resource

## Failure behavior

- Missing Foundry configuration: HTTP 503
- Foundry or MCP execution failure: HTTP 502
- Empty agent output: HTTP 502
- Unexpected MCP tool: request rejected
- Browser network failure: visible connection message in chat
- Long-running call: request fails after the configured timeout rather than hanging indefinitely

## Data model

The public API intentionally exposes a small contract:

```text
CoachRequest
  work_order: string, format SYN-WO-000000
  question: string, 2–4000 characters
  current_step: optional string, up to 120 characters

CoachResponse
  answer: string
  work_order: string

WorkOrderLookupRequest
  work_order: string, format SYN-WO-000000

WorkOrderLookupResponse
  work_order: string
  found: true
  status: optional string
```

No complete WO object is returned to the browser by this gateway.

## Synthetic dataset versions

- `v2.1`: preserved baseline of 120 WOs (`000001`–`000120`)
- `v2.2`: 220 WOs containing the baseline plus 100 intake-teaching records (`000121`–`000220`)

The additional set uses 20 scenario families with five deterministic variants each. Agent-visible records and evaluator-only ground truth remain in separate S3 prefixes. The retrieval Lambda currently points to `agent-input/v2.2/work-orders`; `v2.1` remains unchanged for rollback.

New intake-queue records use `READY_FOR_RESEARCH`. Scenario discrepancies and expected outcomes remain evaluator-only until the researcher works the request; a queued WO must not appear already reviewed.
