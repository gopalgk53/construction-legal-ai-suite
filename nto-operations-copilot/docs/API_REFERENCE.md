# API reference

## Base URLs

Local:

```text
http://localhost:8000
```

Azure:

```text
https://nto-copilot-api-gopalg53.azurewebsites.net
```

## `GET /health`

Returns API availability and whether the Foundry reference has been configured.

### Response

```json
{
  "status": "ok",
  "foundry_configured": true
}
```

This endpoint does not call Foundry or MCP. A successful response proves that the API process is running, not that agent execution is healthy.

## `POST /api/work-orders/lookup`

Confirms that a work order exists through the configured Foundry agent and read-only MCP tool before the frontend changes its active WO.

### Request body

```json
{
  "work_order": "SYN-WO-000023"
}
```

### Successful response

```json
{
  "work_order": "SYN-WO-000023",
  "found": true,
  "status": "UNDER_REVIEW",
  "intake": {
    "customer_name": "Synthetic customer",
    "job_name": "Synthetic Project 023",
    "job_address": "1023 Example Boulevard, Demo City, FL 32023",
    "owner_claimed": "Synthetic owner",
    "general_contractor_claimed": "Synthetic contractor",
    "provided_references": {
      "noc_reference": "SYN-NOC-000023",
      "bond_number": null
    }
  }
}
```

An unknown WO returns `404 Not Found`. Agent, MCP, timeout, or invalid upstream-response failures return `502 Bad Gateway`. The interface must retain the previously confirmed WO until this endpoint succeeds.

## `POST /api/coach`

Retrieves the requested synthetic work-order context through the configured Foundry agent and returns a concise answer to the researcher’s question.

### Request headers

```http
Content-Type: application/json
```

### Request body

```json
{
  "work_order": "SYN-WO-000110",
  "question": "What should I verify?",
  "current_step": "Recorded NOC"
}
```

| Field | Type | Required | Validation |
|---|---|---:|---|
| `work_order` | string | Yes | `SYN-WO-` followed by exactly six digits |
| `question` | string | Yes | 2–4000 characters |
| `current_step` | string or null | No | Maximum 120 characters |

### Successful response

Status: `200 OK`

```json
{
  "answer": "Answer\nVerify...\n\nWhy\nThe evidence...\n\nNext step\nOpen...",
  "work_order": "SYN-WO-000110"
}
```

The answer is requested with these constraints:

- Maximum target of 90 words
- Exactly three headings: `Answer`, `Why`, `Next step`
- No repeated evidence inventory
- Clear distinction between evidence and claims
- Direct statement when the evidence does not establish an answer

## Error responses

### `422 Unprocessable Entity`

The request failed Pydantic validation. The response contains field-level validation details.

### `503 Service Unavailable`

```json
{
  "detail": "Foundry connection is not configured on the server."
}
```

### `502 Bad Gateway`

Possible messages:

```json
{"detail":"The research coach could not respond."}
```

```json
{"detail":"The research coach could not refine its response."}
```

```json
{"detail":"The research coach returned an empty response."}
```

Internal exceptions and credentials are not returned to clients.

## CORS

Allowed browser origins are configured through `FRONTEND_ORIGINS`. The value is a comma-separated exact-origin allowlist.

Example:

```dotenv
FRONTEND_ORIGINS=http://localhost:3000,https://nto-copilot-web-gopalg53.azurewebsites.net
```

## Timeout behavior

Each Foundry Responses call has a 90-second timeout. A coaching request normally performs:

1. Work-order retrieval and evidence-oriented intake
2. A second grounded precision pass

Clients should display a visible loading state and handle network or 502 failures without losing the researcher’s question.

## Example request

```bash
curl -X POST \
  https://nto-copilot-api-gopalg53.azurewebsites.net/api/work-orders/lookup \
  -H 'Content-Type: application/json' \
  -d '{"work_order":"SYN-WO-000023"}'

curl -X POST \
  https://nto-copilot-api-gopalg53.azurewebsites.net/api/coach \
  -H 'Content-Type: application/json' \
  -d '{
    "work_order": "SYN-WO-000110",
    "question": "Why is this a conflict?",
    "current_step": "Recorded NOC"
  }'
```
