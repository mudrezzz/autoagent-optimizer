"""Unit-тесты генератора кода агента."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from optimizer.codegen.agent_generator import AgentCodeGenerator, sanitize_package_name
from optimizer.graph_ir.io import load_graph_ir_spec


def _project_root() -> Path:
    """Возвращает абсолютный путь до корня проекта."""

    return Path(__file__).resolve().parents[2]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw_name", "expected"),
    [
        ("My Agent", "my_agent"),
        ("123-agent", "agent_123_agent"),
        ("___", "generated_agent"),
        ("agent.v1", "agent_v1"),
    ],
)
def test_sanitize_package_name(raw_name: str, expected: str) -> None:
    """Проверяет нормализацию имени сгенерированного Python-пакета."""

    assert sanitize_package_name(raw_name) == expected


@pytest.mark.unit
def test_agent_generator_creates_expected_files(tmp_path: Path) -> None:
    """Проверяет, что генератор создает ключевые файлы runtime-пакета."""

    graph_ir = load_graph_ir_spec(_project_root() / "examples" / "graph_ir" / "direct_llm.ir.json")
    generator = AgentCodeGenerator()
    result = generator.generate(
        graph_ir=graph_ir,
        output_dir=tmp_path,
        package_name="direct_llm_generated",
        force=False,
    )

    assert result.package_dir.exists()
    assert result.graph_ir_file.exists()
    assert result.entrypoint_file.exists()
    assert (result.package_dir / "agent.py").exists()
    assert (result.package_dir / "bindings.py").exists()
    assert (tmp_path / "README.generated.md").exists()

    graph_ir_payload = json.loads(result.graph_ir_file.read_text(encoding="utf-8"))
    assert graph_ir_payload["entry_node"] == graph_ir.entry_node
    assert len(graph_ir_payload["nodes"]) == len(graph_ir.nodes)


@pytest.mark.unit
def test_agent_generator_fails_if_package_exists_without_force(tmp_path: Path) -> None:
    """Проверяет защиту от случайной перезаписи каталога без флага force."""

    graph_ir = load_graph_ir_spec(_project_root() / "examples" / "graph_ir" / "direct_llm.ir.json")
    generator = AgentCodeGenerator()
    generator.generate(graph_ir=graph_ir, output_dir=tmp_path, package_name="existing_agent", force=False)

    with pytest.raises(ValueError):
        generator.generate(graph_ir=graph_ir, output_dir=tmp_path, package_name="existing_agent", force=False)


@pytest.mark.unit
def test_agent_generator_injects_prompt_template_overrides(tmp_path: Path) -> None:
    """Проверяет, что генератор подставляет переданные prompt templates в bindings.py."""

    graph_ir = load_graph_ir_spec(_project_root() / "examples" / "graph_ir" / "direct_llm.ir.json")
    generator = AgentCodeGenerator()
    result = generator.generate(
        graph_ir=graph_ir,
        output_dir=tmp_path,
        package_name="prompt_override_agent",
        prompt_templates_override={"support_answer_v1": "Тестовый prompt шаблон: {query}"},
    )

    bindings_text = (result.package_dir / "bindings.py").read_text(encoding="utf-8")
    assert "Тестовый prompt шаблон: {query}" in bindings_text
