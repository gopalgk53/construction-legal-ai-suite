from __future__ import annotations

import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger("payment_risk_api.metrics")


NAMESPACE = "ConstructionPaymentRisk/API"
REGION = "ap-southeast-2"


API_DIMENSIONS = [
    {
        "Name": "ModelVersion",
        "Value": "logistic-regression-v1",
    },
    {
        "Name": "Environment",
        "Value": "dev",
    },
]


cloudwatch = boto3.client(
    "cloudwatch",
    region_name=REGION,
)


def emit_metric(
    *,
    metric_name: str,
    value: float,
    unit: str = "Count",
    dimensions: list[dict[str, str]] | None = None,
) -> None:
    metric: dict[str, Any] = {
        "MetricName": metric_name,
        "Value": float(value),
        "Unit": unit,
    }

    if dimensions:
        metric["Dimensions"] = dimensions

    try:
        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[metric],
        )

    except (BotoCoreError, ClientError):
        logger.exception(
            "CloudWatch metric emission failed",
            extra={
                "metric_name": metric_name,
            },
        )