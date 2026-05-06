"""Хранилище событий трассировки и расчет сводки по run."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from optimizer.tracing.node_events import NodeEventStatus, NodeExecutionEvent


@dataclass
class InMemoryTraceStore:
    """In-memory trace store для node-level событий текущего процесса."""

    _events_by_run: dict[str, list[NodeExecutionEvent]] = field(default_factory=dict)

    def record(self, event: NodeExecutionEvent) -> None:
        """Сохраняет событие в памяти по ключу `run_id`."""

        run_events = self._events_by_run.setdefault(event.run_id, [])
        run_events.append(event)

    def get_run_events(self, run_id: str) -> list[NodeExecutionEvent]:
        """Возвращает список событий для указанного `run_id`."""

        return list(self._events_by_run.get(run_id, []))

    def get_run_summary(self, *, run_id: str, task_id: str) -> dict[str, Any]:
        """Формирует сводку событий по run для диагностики и CLI-вывода."""

        events = self.get_run_events(run_id)
        started_count = 0
        completed_count = 0
        failed_count = 0
        skipped_count = 0
        unique_nodes: set[str] = set()

        timestamps: list[datetime] = []
        for event in events:
            unique_nodes.add(event.node_id)
            if event.status == NodeEventStatus.STARTED:
                started_count += 1
            elif event.status == NodeEventStatus.COMPLETED:
                completed_count += 1
            elif event.status == NodeEventStatus.FAILED:
                failed_count += 1
            elif event.status == NodeEventStatus.SKIPPED:
                skipped_count += 1

            parsed = _parse_iso_datetime(event.timestamp_utc)
            if parsed is not None:
                timestamps.append(parsed)

        start_time = min(timestamps) if timestamps else None
        end_time = max(timestamps) if timestamps else None
        duration_ms = None
        if start_time is not None and end_time is not None:
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

        return {
            "run_id": run_id,
            "task_id": task_id,
            "events_total": len(events),
            "nodes_touched": len(unique_nodes),
            "started": started_count,
            "completed": completed_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "started_at_utc": start_time.isoformat() if start_time else None,
            "finished_at_utc": end_time.isoformat() if end_time else None,
            "duration_ms": duration_ms,
        }


def _parse_iso_datetime(value: str) -> datetime | None:
    """Безопасно парсит ISO-дату; при ошибке возвращает `None`."""

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None

