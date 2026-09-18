from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ExecutionRecord:
    execution_id: str
    wo_id: str
    status: str = "RUNNING"
    result: Optional[dict[str, Any]] = None
    error_type: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        now = _utc_now()

        if not self.created_at:
            self.created_at = now

        if not self.updated_at:
            self.updated_at = now


class ExecutionStore:
    """
    Thread-safe in-memory execution store.

    Portfolio-v1 implementation only.

    This intentionally sits behind a small interface so it can later be
    replaced by DynamoDB, Redis, or another durable store without changing
    the public API contract.
    """

    def __init__(self) -> None:
        self._records: dict[str, ExecutionRecord] = {}
        self._lock = RLock()

    def create(self, record: ExecutionRecord) -> ExecutionRecord:
        with self._lock:
            if record.execution_id in self._records:
                raise ValueError(
                    f"Execution already exists: {record.execution_id}"
                )

            self._records[record.execution_id] = deepcopy(record)
            return deepcopy(record)

    def get(self, execution_id: str) -> Optional[ExecutionRecord]:
        with self._lock:
            record = self._records.get(execution_id)

            if record is None:
                return None

            return deepcopy(record)

    def update(
        self,
        execution_id: str,
        *,
        status: Optional[str] = None,
        result: Optional[dict[str, Any]] = None,
        error_type: Optional[str] = None,
    ) -> ExecutionRecord:
        with self._lock:
            record = self._records.get(execution_id)

            if record is None:
                raise KeyError(execution_id)

            if status is not None:
                record.status = status

            if result is not None:
                record.result = deepcopy(result)

            if error_type is not None:
                record.error_type = error_type

            record.updated_at = _utc_now()

            return deepcopy(record)


execution_store = ExecutionStore()