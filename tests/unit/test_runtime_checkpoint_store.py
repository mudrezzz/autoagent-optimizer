"""Unit-тесты файлового checkpoint-хранилища runtime."""

from __future__ import annotations

from pathlib import Path

import pytest

from optimizer.renderer.langgraph_dai.checkpoint_store import FileRuntimeCheckpointStore, RuntimeCheckpointStoreError
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState


@pytest.mark.unit
def test_file_runtime_checkpoint_store_save_and_load(tmp_path: Path) -> None:
    """Проверяет сохранение и загрузку checkpoint состояния по task_id."""

    store = FileRuntimeCheckpointStore(tmp_path / "checkpoints")
    state = RenderedGraphState(
        payload={"query": "hello"},
        task_context={"task_id": "task-a", "run_id": "run-a"},
        executed_nodes=["n1"],
    )
    store.save("task-a", state)
    assert store.exists("task-a") is True
    loaded = store.load("task-a")
    assert loaded.task_context["task_id"] == "task-a"
    assert loaded.payload["query"] == "hello"


@pytest.mark.unit
def test_file_runtime_checkpoint_store_requires_non_empty_task_id(tmp_path: Path) -> None:
    """Проверяет валидацию пустого task_id в checkpoint store."""

    store = FileRuntimeCheckpointStore(tmp_path / "checkpoints")
    state = RenderedGraphState(payload={}, task_context={"task_id": "x"})
    with pytest.raises(RuntimeCheckpointStoreError):
        store.save("", state)
    with pytest.raises(RuntimeCheckpointStoreError):
        store.load(" ")


@pytest.mark.unit
def test_file_runtime_checkpoint_store_raises_for_missing_checkpoint(tmp_path: Path) -> None:
    """Проверяет ошибку загрузки при отсутствии checkpoint файла."""

    store = FileRuntimeCheckpointStore(tmp_path / "checkpoints")
    with pytest.raises(RuntimeCheckpointStoreError):
        store.load("missing-task")

