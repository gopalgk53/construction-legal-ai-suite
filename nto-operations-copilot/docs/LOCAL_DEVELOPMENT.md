# Local development

## Prerequisites

- macOS, Linux or Windows with a shell
- Node.js 22+
- npm
- Python 3.12
- Azure CLI
- Access to the configured Microsoft Foundry project

## Authenticate to Azure

```bash
az login
az account show
```

Do not put an Azure access token in `.env`. `DefaultAzureCredential` discovers the Azure CLI session locally and the managed identity in Azure.

## Backend setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The application does not automatically load `.env`; export overrides in the shell when required:

```bash
export AZURE_AI_PROJECT_ENDPOINT='https://RESOURCE.services.ai.azure.com/api/projects/PROJECT'
export AZURE_AI_AGENT_NAME='wo-intake-agent'
export AZURE_AI_AGENT_VERSION='3'
export FRONTEND_ORIGINS='http://localhost:3000,http://localhost:3001'
```

Start the API:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Verify it:

```bash
curl http://127.0.0.1:8000/health
```

Expected result:

```json
{"status":"ok","foundry_configured":true}
```

## Frontend setup

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

`frontend/.env.local` should contain:

```dotenv
NEXT_PUBLIC_NTO_API_BASE_URL=http://localhost:8000
```

Open the local URL printed by Next.js. It is normally port 3000; another port can be selected when that port is already occupied.

## Test a live question

Use a known synthetic work order:

```bash
curl -X POST http://127.0.0.1:8000/api/coach \
  -H 'Content-Type: application/json' \
  -d '{
    "work_order": "SYN-WO-000110",
    "question": "What should I verify?",
    "current_step": "Recorded NOC"
  }'
```

The answer should be concise and contain `Answer`, `Why`, and `Next step`.

## Common local problems

### `Failed to fetch`

The frontend cannot reach the API. Confirm that port 8000 is listening and `NEXT_PUBLIC_NTO_API_BASE_URL` is correct.

### CORS error

Add the exact frontend origin to `FRONTEND_ORIGINS` and restart the API.

### Azure authentication failure

Run `az login`, confirm the active subscription, and verify that the signed-in identity has access to the Foundry project.

### MCP endpoint returns 401 directly

This is expected when calling the AWS endpoint without its authorization. The application does not call it directly from the browser or gateway; the configured Foundry agent owns the MCP connection.

### Slow first response

The request performs agent execution, MCP retrieval and a second precision pass. Local and free-tier cold starts can add latency.
