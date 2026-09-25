import json
import os
from contextlib import asynccontextmanager

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


PROJECT_ENDPOINT = os.environ.get(
    "AZURE_AI_PROJECT_ENDPOINT",
    "https://gopalg53-5366-resource.services.ai.azure.com/api/projects/gopalg53-5366",
).strip()
AGENT_NAME = os.environ.get("AZURE_AI_AGENT_NAME", "wo-intake-agent").strip()
AGENT_VERSION = os.environ.get("AZURE_AI_AGENT_VERSION", "3").strip()
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:3002",
    ).split(",")
    if origin.strip()
]

credential: DefaultAzureCredential | None = None
project_client: AIProjectClient | None = None
openai_client = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global credential, project_client, openai_client
    if PROJECT_ENDPOINT:
        credential = DefaultAzureCredential()
        project_client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
        openai_client = project_client.get_openai_client()
    yield
    if project_client:
        project_client.close()
    if credential:
        credential.close()


app = FastAPI(title="NTO Operations Copilot API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class CoachRequest(BaseModel):
    work_order: str = Field(pattern=r"^SYN-WO-\d{6}$")
    question: str = Field(min_length=2, max_length=4000)
    current_step: str | None = Field(default=None, max_length=120)


class CoachResponse(BaseModel):
    answer: str
    work_order: str


class WorkOrderLookupRequest(BaseModel):
    work_order: str = Field(pattern=r"^SYN-WO-\d{6}$")


class WorkOrderLookupResponse(BaseModel):
    work_order: str
    found: bool
    status: str | None = None
    intake: dict | None = None


def approval_requests(response):
    return [
        item
        for item in response.output
        if getattr(item, "type", None) == "mcp_approval_request"
    ]


def approve_work_order_lookup(response):
    for _ in range(3):
        requests = approval_requests(response)
        if not requests:
            return response

        approvals = []
        for request in requests:
            identity = (
                getattr(request, "server_label", None),
                getattr(request, "name", None),
            )
            if identity != ("sunray-wo-mcp", "get_work_order"):
                raise RuntimeError(f"Unapproved MCP tool requested: {identity}")
            approvals.append(
                {
                    "type": "mcp_approval_response",
                    "approve": True,
                    "approval_request_id": request.id,
                }
            )

        response = openai_client.responses.create(
            previous_response_id=response.id,
            input=approvals,
            extra_body={
                "agent_reference": {
                    "name": AGENT_NAME,
                    "version": AGENT_VERSION,
                    "type": "agent_reference",
                }
            },
            timeout=90,
        )

    raise RuntimeError("The agent exceeded the MCP approval limit.")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "foundry_configured": bool(PROJECT_ENDPOINT and AGENT_NAME and AGENT_VERSION),
    }


@app.post("/api/work-orders/lookup", response_model=WorkOrderLookupResponse)
def lookup_work_order(request: WorkOrderLookupRequest):
    if not openai_client or not AGENT_NAME or not AGENT_VERSION:
        raise HTTPException(
            status_code=503,
            detail="Foundry connection is not configured on the server.",
        )

    message = f"""Retrieve synthetic Work Order {request.work_order} using get_work_order.
Return valid JSON only using this exact shape and values from the retrieved work order:
{{"work_order":"{request.work_order}","found":true,"status":null,"intake":{{"customer_name":null,"job_name":null,"job_address":null,"project_type_claimed":null,"type_of_work":null,"first_day_on_job":null,"job_amount":null,"owner_claimed":null,"general_contractor_claimed":null,"provided_references":{{"permit_number":null,"noc_reference":null,"parcel_or_folio":null,"bond_number":null}}}}}}
Replace nulls only when that value exists in the retrieved work order. Use its actual research status for status. Do not infer missing facts and do not return placeholder text.
If the tool reports that the work order does not exist, return:
{{"work_order":"{request.work_order}","found":false,"status":null,"intake":null}}
Do not analyze the work order and do not include markdown."""

    try:
        response = openai_client.responses.create(
            input=[{"role": "user", "content": message}],
            extra_body={
                "agent_reference": {
                    "name": AGENT_NAME,
                    "version": AGENT_VERSION,
                    "type": "agent_reference",
                }
            },
            timeout=90,
        )
        response = approve_work_order_lookup(response)
        raw = (getattr(response, "output_text", "") or "").strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```json").removeprefix("```")
            raw = raw.removesuffix("```").strip()
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="The work-order lookup returned an invalid response.") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The work order could not be retrieved.") from exc

    found = bool(result.get("found"))
    if not found:
        raise HTTPException(status_code=404, detail=f"Work order {request.work_order} was not found.")

    status = result.get("status")
    if status == "STATUS_IF_AVAILABLE":
        status = None

    return WorkOrderLookupResponse(
        work_order=str(result.get("work_order") or request.work_order),
        found=True,
        status=status,
        intake=result.get("intake"),
    )


@app.post("/api/coach", response_model=CoachResponse)
def coach(request: CoachRequest):
    if not openai_client or not AGENT_NAME or not AGENT_VERSION:
        raise HTTPException(
            status_code=503,
            detail="Foundry connection is not configured on the server.",
        )

    message = f"""A new NTO researcher is working on work order {request.work_order}.
Current research step: {request.current_step or 'not specified'}.
Researcher's question or issue:
{request.question}

Use the configured read-only work-order tool when work-order facts are needed.
Teach the approved process step by step. Separate customer claims from verified
evidence, state uncertainty, never invent missing facts, and identify when human
review or escalation is required. Keep the response concise and operational."""

    try:
        response = openai_client.responses.create(
            input=[{"role": "user", "content": message}],
            extra_body={
                "agent_reference": {
                    "name": AGENT_NAME,
                    "version": AGENT_VERSION,
                    "type": "agent_reference",
                }
            },
            timeout=90,
        )
        response = approve_work_order_lookup(response)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The research coach could not respond.") from exc

    evidence_report = getattr(response, "output_text", "") or ""
    if not evidence_report.strip():
        raise HTTPException(status_code=502, detail="The research coach returned an empty response.")

    precision_prompt = f"""Answer the researcher's exact question using only the work-order evidence you just retrieved.

Question: {request.question}

Response rules:
- Do not repeat the work-order report, customer claims, or evidence inventory.
- Answer only what was asked.
- Use no more than 90 words.
- Use exactly these headings: Answer, Why, Next step.
- Use one or two short sentences under each heading.
- Clearly distinguish verified evidence from an unverified claim.
- If the evidence does not establish the answer, say so directly.
- Do not add background information that the researcher did not request."""

    try:
        concise_response = openai_client.responses.create(
            previous_response_id=response.id,
            input=[{"role": "user", "content": precision_prompt}],
            extra_body={
                "agent_reference": {
                    "name": AGENT_NAME,
                    "version": AGENT_VERSION,
                    "type": "agent_reference",
                }
            },
            timeout=90,
        )
        concise_response = approve_work_order_lookup(concise_response)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The research coach could not refine its response.") from exc

    answer = getattr(concise_response, "output_text", "") or ""
    if not answer.strip():
        raise HTTPException(status_code=502, detail="The research coach returned an empty response.")

    return CoachResponse(answer=answer.strip(), work_order=request.work_order)
