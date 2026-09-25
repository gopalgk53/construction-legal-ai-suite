# NTO Operations Copilot

NTO Operations Copilot is an evidence-grounded research coach for new Notice to Owner researchers. It guides a researcher through the complete operational process, retrieves synthetic work-order evidence through an approved read-only MCP tool, explains exceptions, and recommends the next approved action without replacing human verification.

## Live deployment

- Frontend: <https://nto-copilot-web-gopalg53.azurewebsites.net>
- API health: <https://nto-copilot-api-gopalg53.azurewebsites.net/health>
- Azure region: Southeast Asia
- Hosting: Azure App Service Free plan

## Product principles

- Teach the process instead of silently doing the researcher’s work.
- Keep the researcher in control of verification and escalation.
- Separate customer claims from independently documented evidence.
- Preserve conflicts rather than selecting a convenient value.
- State uncertainty and missing information explicitly.
- Use only the approved read-only work-order retrieval tool.
- Return short, query-specific coaching answers.

## Research workflow

The interface guides the researcher through six stages:

1. Understand the request
2. Confirm the property
3. Locate and validate the recorded NOC
4. Verify project participants
5. Prepare the notice from supported fields
6. Complete quality control

The researcher enters a work-order identifier, selects the current stage, and explains the problem in their own words. The coach retrieves the relevant work-order evidence and responds using three sections: `Answer`, `Why`, and `Next step`.

## Architecture

```text
Researcher
    |
    v
Next.js frontend
    |
    | POST /api/coach
    v
FastAPI gateway
    |
    | Managed identity / DefaultAzureCredential
    v
Microsoft Foundry project
    |
    | wo-intake-agent:v3
    v
Approved MCP tool
sunray-wo-mcp.get_work_order
    |
    v
Synthetic AWS work-order data
```

The browser never receives Azure credentials, MCP authorization material, or direct Foundry access. See [Architecture](docs/ARCHITECTURE.md) for the detailed request lifecycle.

## Repository structure

```text
nto-operations-copilot/
├── backend/                  FastAPI Foundry gateway
├── docs/                     Architecture, deployment and operations guides
├── evaluation/               Reserved for evaluation artifacts
├── frontend/                 Next.js research-coach interface
└── knowledge/                Approved NTO operating knowledge
    ├── 01-operations-sop.pdf
    ├── 02-research-decision-escalation.md
    └── 03-qc-checklist.md
```

## Technology

- Next.js 16, React 19 and TypeScript
- Tailwind CSS 4
- Framer Motion and Lucide React
- FastAPI and Pydantic
- Azure AI Projects and Azure Identity
- Microsoft Foundry Responses API
- MCP-based synthetic work-order retrieval
- Azure App Service with managed identity

## Quick start

Prerequisites:

- Node.js 22 or newer
- Python 3.12
- Azure CLI authenticated to an account with Foundry project access

Start the API:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
cp .env.example .env.local
npm ci
npm run dev
```

Open <http://localhost:3000>. See [Local development](docs/LOCAL_DEVELOPMENT.md) for authentication and troubleshooting details.

## API example

```bash
curl -X POST http://localhost:8000/api/coach \
  -H 'Content-Type: application/json' \
  -d '{
    "work_order": "SYN-WO-000110",
    "question": "What should I verify?",
    "current_step": "Recorded NOC"
  }'
```

Successful response:

```json
{
  "answer": "Answer\n...\n\nWhy\n...\n\nNext step\n...",
  "work_order": "SYN-WO-000110"
}
```

## Validation

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

Backend syntax check:

```bash
python -m py_compile backend/app.py
```

Live checks and acceptance criteria are documented in [Testing](docs/TESTING.md).

## Documentation

- [Documentation index](docs/README.md)
- [User guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API reference](docs/API_REFERENCE.md)
- [Local development](docs/LOCAL_DEVELOPMENT.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Operations runbook](docs/OPERATIONS.md)
- [Security and trust boundaries](docs/SECURITY.md)
- [Testing and acceptance](docs/TESTING.md)
- [Frontend guide](frontend/README.md)
- [Backend guide](backend/README.md)

## Current limitations

- The work-order source contains synthetic demonstration data.
- The coach currently uses `wo-intake-agent:v3`; the full evidence report is retained server-side and a second grounded pass produces the concise answer.
- Responses can take tens of seconds because they include Foundry execution and MCP retrieval.
- The free Azure hosting tier can cold-start after inactivity.
- Chat history is held in component state and is not persisted.
- The frontend does not yet provide user authentication or role-based access.

## Git policy

Deployment and documentation were created without committing or pushing. Review all local changes before creating your own commit.
