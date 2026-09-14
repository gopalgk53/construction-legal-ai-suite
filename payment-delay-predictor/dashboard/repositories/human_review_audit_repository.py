import json
from datetime import datetime, timezone

import boto3


class HumanReviewAuditRepository:
    """
    Persist human review records to S3.

    Reviews are written as separate immutable JSON
    objects for auditability.
    """

    def __init__(
        self,
        bucket_name: str = "construction-payment-risk-dev-gk53",
        prefix: str = "artifacts/dashboard/payment-risk-dashboard/v1/human-reviews",
        region_name: str = "ap-southeast-2",
    ):
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/")
        self.s3 = boto3.client(
            "s3",
            region_name=region_name,
        )

    def build_object_key(
        self,
        review: dict,
    ) -> str:

        reviewed_at = review["reviewed_at"]

        reviewed_dt = datetime.fromisoformat(
            reviewed_at.replace(
                "Z",
                "+00:00",
            )
        )

        return (
            f"{self.prefix}/"
            f"{reviewed_dt.year:04d}/"
            f"{reviewed_dt.month:02d}/"
            f"{reviewed_dt.day:02d}/"
            f"{review['workflow_id']}/"
            f"{review['review_id']}.json"
        )

    def save_review(
        self,
        review: dict,
    ) -> dict:

        key = self.build_object_key(
            review
        )

        payload = json.dumps(
            review,
            indent=2,
            sort_keys=True,
        ).encode(
            "utf-8"
        )

        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=payload,
            ContentType="application/json",
        )

        return {
            "bucket":
                self.bucket_name,

            "key":
                key,

            "review_id":
                review[
                    "review_id"
                ],

            "workflow_id":
                review[
                    "workflow_id"
                ],

            "persisted_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }

    def get_review(
        self,
        key: str,
    ) -> dict:

        response = self.s3.get_object(
            Bucket=self.bucket_name,
            Key=key,
        )

        body = (
            response[
                "Body"
            ]
            .read()
            .decode(
                "utf-8"
            )
        )

        return json.loads(
            body
        )
