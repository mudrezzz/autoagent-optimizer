"""Unit-тесты in-memory trace store и моделей событий."""

from __future__ import annotations

import pytest

from optimizer.tracing.node_events import NodeEventStatus, NodeExecutionEvent
from optimizer.tracing.trace_store import InMemoryTraceStore


@pytest.mark.unit
def test_trace_store_aggregates_summary_counts() -> None:
    """Проверяет агрегирование started/completed/failed/skipped в сводке run."""

    store = InMemoryTraceStore()
    run_id = "run-1"
    task_id = "task-1"
    store.record(
        NodeExecutionEvent(
            run_id=run_id,
            task_id=task_id,
            node_id="a",
            status=NodeEventStatus.STARTED,
            timestamp_utc="2026-05-06T10:00:00+00:00",
        )
    )
    store.record(
        NodeExecutionEvent(
            run_id=run_id,
            task_id=task_id,
            node_id="a",
            status=NodeEventStatus.COMPLETED,
            timestamp_utc="2026-05-06T10:00:01+00:00",
        )
    )
    store.record(
        NodeExecutionEvent(
            run_id=run_id,
            task_id=task_id,
            node_id="b",
            status=NodeEventStatus.SKIPPED,
            timestamp_utc="2026-05-06T10:00:02+00:00",
        )
    )
    store.record(
        NodeExecutionEvent(
            run_id=run_id,
            task_id=task_id,
            node_id="c",
            status=NodeEventStatus.FAILED,
            timestamp_utc="2026-05-06T10:00:03+00:00",
            error="boom",
        )
    )

    summary = store.get_run_summary(run_id=run_id, task_id=task_id)
    assert summary["events_total"] == 4
    assert summary["started"] == 1
    assert summary["completed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 1
    assert summary["nodes_touched"] == 3
    assert summary["duration_ms"] == 3000

