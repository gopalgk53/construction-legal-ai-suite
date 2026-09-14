import time

import boto3

from dashboard.config import (
    AWS_REGION,
    ATHENA_DATABASE,
    ATHENA_TABLE,
    ATHENA_OUTPUT,
    ATHENA_POLL_INTERVAL_SECONDS,
)


class AthenaRepository:
    """Read-only Athena repository for dashboard analytics."""

    def __init__(self):
        self.client = boto3.client(
            "athena",
            region_name=AWS_REGION,
        )

    def execute_query(
        self,
        sql: str,
    ) -> list[dict]:
        """
        Execute an Athena query and return rows as dictionaries.
        """

        response = self.client.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={
                "Database": ATHENA_DATABASE,
            },
            ResultConfiguration={
                "OutputLocation": ATHENA_OUTPUT,
            },
        )

        execution_id = response[
            "QueryExecutionId"
        ]

        while True:
            execution = (
                self.client.get_query_execution(
                    QueryExecutionId=execution_id
                )
            )

            status = execution[
                "QueryExecution"
            ]["Status"]["State"]

            if status == "SUCCEEDED":
                break

            if status in {
                "FAILED",
                "CANCELLED",
            }:
                reason = execution[
                    "QueryExecution"
                ]["Status"].get(
                    "StateChangeReason",
                    "Unknown Athena error",
                )

                raise RuntimeError(
                    f"Athena query {status}: "
                    f"{reason}"
                )

            time.sleep(
                ATHENA_POLL_INTERVAL_SECONDS
            )

        paginator = (
            self.client.get_paginator(
                "get_query_results"
            )
        )

        raw_rows = []

        for page in paginator.paginate(
            QueryExecutionId=execution_id
        ):
            raw_rows.extend(
                page["ResultSet"]["Rows"]
            )

        if not raw_rows:
            return []

        headers = [
            column.get(
                "VarCharValue",
                "",
            )
            for column in raw_rows[0]["Data"]
        ]

        results = []

        for row in raw_rows[1:]:
            values = [
                column.get(
                    "VarCharValue"
                )
                for column in row["Data"]
            ]

            values += [
                None
            ] * (
                len(headers) - len(values)
            )

            results.append(
                dict(
                    zip(
                        headers,
                        values,
                    )
                )
            )

        return results

    def get_portfolio_kpis(
        self,
    ) -> dict:
        """Return governed portfolio-level operational KPIs."""

        sql = f"""
        SELECT
            COUNT(*) AS total_workflows,

            AVG(
                payment_chain_completeness_score
            ) AS avg_chain_completeness,

            AVG(
                research_confidence_score
            ) AS avg_research_confidence,

            SUM(
                CASE
                    WHEN critical_field_missing = 1
                    THEN 1
                    ELSE 0
                END
            ) AS critical_missing_count,

            SUM(
                CASE
                    WHEN multiple_candidate_records = 1
                    THEN 1
                    ELSE 0
                END
            ) AS multiple_candidate_count,

            SUM(
                CASE
                    WHEN conflicting_project_information = 1
                    THEN 1
                    ELSE 0
                END
            ) AS conflicting_info_count,

            SUM(
                CASE
                    WHEN deadline_days_remaining <= 15
                    THEN 1
                    ELSE 0
                END
            ) AS deadline_15d_count

        FROM {ATHENA_TABLE}
        """

        rows = self.execute_query(sql)

        return rows[0] if rows else {}

    def get_state_segments(
        self,
    ) -> list[dict]:
        """Return state-level operational analytics."""

        sql = f"""
        SELECT
            state,

            COUNT(*) AS workflow_count,

            AVG(
                payment_chain_completeness_score
            ) AS avg_chain_completeness,

            AVG(
                research_confidence_score
            ) AS avg_research_confidence,

            SUM(
                CASE
                    WHEN critical_field_missing = 1
                    THEN 1
                    ELSE 0
                END
            ) AS critical_missing_count

        FROM {ATHENA_TABLE}

        GROUP BY state

        ORDER BY workflow_count DESC
        """

        return self.execute_query(sql)

    def get_candidate_workflows(
        self,
        limit: int = 100,
    ) -> list[dict]:
        """
        Return candidate workflows for operational review.

        Candidate selection is operational filtering,
        not model inference.
        """

        if not 1 <= limit <= 500:
            raise ValueError(
                "limit must be between 1 and 500"
            )

        sql = f"""
        SELECT
            record_id,
            project_id,
            assessment_date,

            state,
            project_type,
            public_private,
            customer_role,
            hiring_party_type,

            payment_chain_completeness_score,
            research_confidence_score,
            deadline_days_remaining,
            prior_escalation_rate,
            prior_projects_with_hiring_party,
            expected_party_count,

            critical_field_missing,
            multiple_candidate_records,
            conflicting_project_information

        FROM {ATHENA_TABLE}

        ORDER BY
            critical_field_missing DESC,
            conflicting_project_information DESC,
            multiple_candidate_records DESC,
            deadline_days_remaining ASC

        LIMIT {limit}
        """

        return self.execute_query(sql)
