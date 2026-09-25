# Backend

The backend is a FastAPI gateway between the browser and Microsoft Foundry. It protects credentials, enforces the MCP tool allowlist, retrieves synthetic WO evidence through `wo-intake-agent:v3`, and returns a concise grounded coaching answer.

## Endpoints

### `GET /health`

Returns service and Foundry configuration status.

### `POST /api/coach`

Request:

```json
{
  "work_order": "SYN-WO-000110",
  "question": "What should I verify?",
  "current_step": "Recorded NOC"
}
```

Response:

```json
{
  "answer": "Answer\n...\n\nWhy\n...\n\nNext step\n...",
  "work_order": "SYN-WO-000110"
}
```

## Environment

See `.env.example` for all configuration fields. Authentication is provided by `DefaultAzureCredential`; do not add a token or client secret to the repository.

## Run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## Safety policy

Only `sunray-wo-mcp.get_work_order` is auto-approved. Any other MCP tool request is rejected.

See the repository [Architecture](../docs/ARCHITECTURE.md), [Security](../docs/SECURITY.md) and [Operations](../docs/OPERATIONS.md) documents.
