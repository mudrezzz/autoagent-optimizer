"""Файловое checkpoint-хранилище runtime состояния Graph IR workflow."""

from __future__ import annotations

import re
from pathlib import Path

from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState


class RuntimeCheckpointStoreError(ValueError):
    """Ошибка операций checkpoint-хранилища runtime состояния."""


class FileRuntimeCheckpointStore:
    """Файловое checkpoint-хранилище, сохраняющее state по `task_id`."""

    def __init__(self, base_dir: Path) -> None:
        """Инициализирует хранилище и создает директорию при необходимости."""

        self._base_dir = base_dir.resolve()
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, task_id: str, state: RenderedGraphState) -> Path:
        """Сохраняет checkpoint состояния для task_id и возвращает путь до файла."""

        resolved_task_id = _validate_task_id(task_id)
        path = self._checkpoint_path(resolved_task_id)
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, task_id: str) -> RenderedGraphState:
        """Загружает checkpoint состояния по task_id."""

        resolved_task_id = _validate_task_id(task_id)
        path = self._checkpoint_path(resolved_task_id)
        if not path.exists():
            raise RuntimeCheckpointStoreError(f"Checkpoint для task_id `{resolved_task_id}` не найден: {path}")
        return RenderedGraphState.model_validate_json(path.read_text(encoding="utf-8"))

    def exists(self, task_id: str) -> bool:
        """Проверяет наличие checkpoint-файла для task_id."""

        resolved_task_id = _validate_task_id(task_id)
        return self._checkpoint_path(resolved_task_id).exists()

    def delete(self, task_id: str) -> None:
        """Удаляет checkpoint по task_id, если он существует."""

        resolved_task_id = _validate_task_id(task_id)
        path = self._checkpoint_path(resolved_task_id)
        if path.exists():
            path.unlink()

    def _checkpoint_path(self, task_id: str) -> Path:
        """Возвращает путь checkpoint-файла для task_id."""

        safe = _safe_file_part(task_id)
        return self._base_dir / f"{safe}.checkpoint.json"


def _validate_task_id(task_id: str) -> str:
    """Проверяет, что task_id непустой и пригоден для checkpoint-контракта."""

    resolved = str(task_id).strip()
    if not resolved:
        raise RuntimeCheckpointStoreError("task_id обязателен для checkpoint/resume пути.")
    return resolved


def _safe_file_part(value: str) -> str:
    """Нормализует task_id в безопасное имя файла."""

    collapsed = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value)
    collapsed = collapsed.strip("._-")
    return collapsed or "task"

