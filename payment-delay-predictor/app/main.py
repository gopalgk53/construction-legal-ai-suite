from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.observability import (
    RequestTimer,
    emit_structured_log,
    generate_request_id,
)

from app.config import (
    MODEL_VERSION,
    FEATURE_CONTRACT_VERSION,
    FINAL_THRESHOLD,
)

from app.schemas import (
    PredictionRequest,
    PredictionResponse,
    HealthResponse,
    ModelMetadataResponse,
)

from app.inference import (
    predict_workflow,
)

from app.metrics import (
    API_DIMENSIONS,
    emit_metric,
)
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title="Construction Payment Risk Prediction API",
    description=(
        "Operational risk scoring service for "
        "construction payment-protection workflows."
    ),
    version="1.0.0",
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = getattr(
        request.state,
        "request_id",
        generate_request_id(),
    )

    errors = exc.errors()

    missing_count = sum(
        1
        for error in errors
        if error.get("type") == "missing"
    )

    emit_metric(
        metric_name="ClientErrorCount",
        value=1,
        unit="Count",
        dimensions=API_DIMENSIONS,
    )

    emit_metric(
        metric_name="ValidationFailureCount",
        value=1,
        unit="Count",
        dimensions=API_DIMENSIONS,
    )

    if missing_count:
        emit_metric(
            metric_name="MissingRequiredFieldCount",
            value=missing_count,
            unit="Count",
            dimensions=API_DIMENSIONS,
        )

    emit_structured_log(
        event_type="validation_failure",
        request_id=request_id,
        http_status=422,
        latency_ms=0.0,
        extra={
            "error_count": len(errors),
            "missing_field_count": missing_count,
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "request_id": request_id,
        },
    )


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health():
    return {
        "status": "ok"
    }


@app.get(
    "/v1/model",
    response_model=ModelMetadataResponse,
)
def model_metadata():
    return {
        "model_version":
            MODEL_VERSION,

        "feature_contract_version":
            FEATURE_CONTRACT_VERSION,

        "threshold":
            FINAL_THRESHOLD,

        "status":
            "APPROVED_CHAMPION",
    }


@app.post(
    "/v1/predict",
    response_model=PredictionResponse,
)
def predict(
    request_data: PredictionRequest,
    request: Request,
):
    try:
        result = predict_workflow(
            request_data
        )
        emit_metric(
            metric_name="PredictionCount",
            value=1,
            unit="Count",
            dimensions=API_DIMENSIONS,
        )
        
        if result["model_decision"] == "FLAGGED_BY_MODEL":
            emit_metric(
                metric_name="FlaggedCount",
                value=1,
                unit="Count",
                dimensions=API_DIMENSIONS,
            )

        emit_structured_log(
            event_type="prediction",
            request_id=request.state.request_id,
            http_status=200,
            latency_ms=0.0,
            model_version=result["model_version"],
            predicted_risk=result[
                "predicted_operational_risk"
            ],
            model_decision=result[
                "model_decision"
            ],
        )

        risk = float(
            result["predicted_operational_risk"]
        )
        
        emit_metric(
            metric_name="PredictionCount",
            value=1,
            unit="Count",
            dimensions=API_DIMENSIONS,
        )
        
        emit_metric(
            metric_name="PredictedRisk",
            value=risk,
            unit="None",
            dimensions=API_DIMENSIONS,
        )
        
        if result["model_decision"] == "FLAGGED_BY_MODEL":
            emit_metric(
                metric_name="FlaggedCount",
                value=1,
                unit="Count",
                dimensions=API_DIMENSIONS,
            )
        
        if risk < 0.20:
            risk_band_metric = "LowRiskCount"
        
        elif risk < 0.50:
            risk_band_metric = "MediumRiskCount"
        
        else:
            risk_band_metric = "HighRiskCount"
        
        emit_metric(
            metric_name=risk_band_metric,
            value=1,
            unit="Count",
            dimensions=API_DIMENSIONS,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction service encountered "
                "an internal error."
            ),
        ) from exc

@app.middleware("http")
async def observability_middleware(
    request: Request,
    call_next,
):
    request_id = generate_request_id()

    # Make the same ID available to endpoints.
    request.state.request_id = request_id

    timer = RequestTimer()

    try:
        response = await call_next(request)

        latency_ms = timer.elapsed_ms()

        emit_metric(
            metric_name="RequestCount",
            value=1,
            unit="Count",
            dimensions=API_DIMENSIONS,
        )
        
        emit_metric(
            metric_name="LatencyMs",
            value=latency_ms,
            unit="Milliseconds",
            dimensions=API_DIMENSIONS,
        )
        
        if response.status_code >= 500:
            emit_metric(
                metric_name="ServerErrorCount",
                value=1,
                unit="Count",
                dimensions=API_DIMENSIONS,
            )

        emit_structured_log(
            event_type="http_request",
            request_id=request_id,
            http_status=response.status_code,
            latency_ms=latency_ms,
            extra={
                "method": request.method,
                "path": request.url.path,
            },
        )

        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:
        latency_ms = timer.elapsed_ms()

        emit_structured_log(
            event_type="http_request_error",
            request_id=request_id,
            http_status=500,
            latency_ms=latency_ms,
            extra={
                "method": request.method,
                "path": request.url.path,
            },
        )
        emit_metric(
            metric_name="ServerErrorCount",
            value=1,
            unit="Count",
            dimensions=API_DIMENSIONS,
        )

        raise