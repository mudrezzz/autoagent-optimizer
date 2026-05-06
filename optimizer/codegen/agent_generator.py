"""Генерация исполняемого Python-агента из Graph IR."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from optimizer.graph_ir.models import GraphIRSpec, GraphNodeKind


@dataclass
class AgentCodegenResult:
    """Результат генерации кодового пакета агента."""

    output_dir: Path
    package_dir: Path
    package_name: str
    graph_ir_file: Path
    entrypoint_file: Path
    generated_files: list[Path]

    def summary(self) -> dict[str, str | list[str]]:
        """Возвращает компактную сводку для CLI и логов."""

        return {
            "output_dir": str(self.output_dir),
            "package_dir": str(self.package_dir),
            "package_name": self.package_name,
            "graph_ir_file": str(self.graph_ir_file),
            "entrypoint_file": str(self.entrypoint_file),
            "generated_files": [str(path) for path in self.generated_files],
        }


class AgentCodeGenerator:
    """Генератор кода агента, который собирает runtime-пакет из Graph IR."""

    def generate(
        self,
        *,
        graph_ir: GraphIRSpec,
        output_dir: Path,
        package_name: str,
        force: bool = False,
    ) -> AgentCodegenResult:
        """Генерирует пакет агента и скрипт запуска в указанный каталог."""

        resolved_output_dir = output_dir.resolve()
        resolved_package_name = sanitize_package_name(package_name)
        package_dir = resolved_output_dir / resolved_package_name

        if package_dir.exists():
            if not force:
                raise ValueError(
                    f"Каталог пакета уже существует: {package_dir}. "
                    "Используйте --force для перезаписи."
                )
            shutil.rmtree(package_dir)

        package_dir.mkdir(parents=True, exist_ok=True)
        resolved_output_dir.mkdir(parents=True, exist_ok=True)

        graph_ir_file = package_dir / "graph_ir.json"
        graph_ir_file.write_text(graph_ir.model_dump_json(indent=2), encoding="utf-8")

        init_file = package_dir / "__init__.py"
        init_file.write_text(self._render_package_init(), encoding="utf-8")

        bindings_file = package_dir / "bindings.py"
        bindings_file.write_text(self._render_bindings(graph_ir), encoding="utf-8")

        agent_file = package_dir / "agent.py"
        agent_file.write_text(self._render_agent_class(), encoding="utf-8")

        entrypoint_file = resolved_output_dir / "run_generated_agent.py"
        entrypoint_file.write_text(self._render_entrypoint(resolved_package_name), encoding="utf-8")

        readme_file = resolved_output_dir / "README.generated.md"
        readme_file.write_text(self._render_readme(resolved_package_name), encoding="utf-8")

        generated_files = [graph_ir_file, init_file, bindings_file, agent_file, entrypoint_file, readme_file]
        return AgentCodegenResult(
            output_dir=resolved_output_dir,
            package_dir=package_dir,
            package_name=resolved_package_name,
            graph_ir_file=graph_ir_file,
            entrypoint_file=entrypoint_file,
            generated_files=generated_files,
        )

    def _render_package_init(self) -> str:
        """Формирует содержимое `__init__.py` для сгенерированного пакета."""

        return (
            '"""Сгенерированный пакет агента AutoAgent Optimizer."""\n\n'
            "from .agent import GeneratedAgent\n\n"
            '__all__ = ["GeneratedAgent"]\n'
        )

    def _render_bindings(self, graph_ir: GraphIRSpec) -> str:
        """Формирует модуль биндингов с fallback-логикой по component_ref."""

        prompt_ids = sorted(_collect_prompt_ids(graph_ir))
        deterministic_refs = sorted(_collect_component_refs(graph_ir, GraphNodeKind.DETERMINISTIC))
        tool_refs = sorted(_collect_component_refs(graph_ir, GraphNodeKind.TOOL))
        validator_refs = sorted(_collect_component_refs(graph_ir, GraphNodeKind.VALIDATOR))
        hitl_refs = sorted(_collect_component_refs(graph_ir, GraphNodeKind.HITL_GATE))

        prompt_lines = "\n".join(
            [f'        "{prompt_id}": "TODO: Опишите prompt шаблон для {prompt_id}.",' for prompt_id in prompt_ids]
        )
        if not prompt_lines:
            prompt_lines = "        # В этом графе нет узлов с prompt_id."

        deterministic_lines = _render_registry_lines(deterministic_refs, "_default_fallback")
        tool_lines = _render_registry_lines(tool_refs, "_default_fallback")
        validator_lines = _render_registry_lines(validator_refs, "_validator_fallback")
        hitl_lines = _render_registry_lines(hitl_refs, "_hitl_fallback")

        return f'''"""Биндинги сгенерированного агента: prompt templates и обработчики component_ref."""

from __future__ import annotations

import importlib
from typing import Any, Callable

from optimizer.renderer.langgraph_dai.adapter import RendererBindings
from optimizer.renderer.langgraph_dai.runtime_state import RenderedGraphState

NodeCallable = Callable[[RenderedGraphState, Any], Any]


def build_bindings() -> RendererBindings:
    """Собирает объект RendererBindings для запуска сгенерированного агента."""

    prompt_templates: dict[str, str] = {{
{prompt_lines}
    }}

    deterministic_registry: dict[str, NodeCallable] = {{
{deterministic_lines}
    }}
    tool_registry: dict[str, NodeCallable] = {{
{tool_lines}
    }}
    validator_registry: dict[str, NodeCallable] = {{
{validator_lines}
    }}
    hitl_registry: dict[str, NodeCallable] = {{
{hitl_lines}
    }}

    return RendererBindings(
        prompt_templates=prompt_templates,
        deterministic_registry=deterministic_registry,
        tool_registry=tool_registry,
        validator_registry=validator_registry,
        hitl_registry=hitl_registry,
    )


def _resolve_python_callable_or_fallback(component_ref: str, fallback: NodeCallable) -> NodeCallable:
    """Пытается загрузить `python://module:function`, иначе возвращает fallback."""

    if not component_ref.startswith("python://"):
        return fallback
    raw = component_ref[len("python://") :]
    if ":" not in raw:
        return fallback

    module_name, func_name = raw.split(":", 1)
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name, None)
        if callable(func):
            return func
    except Exception:
        # Если пользовательский модуль пока не реализован, остаемся на fallback.
        return fallback
    return fallback


def _default_fallback(_state: RenderedGraphState, node: Any) -> dict[str, Any]:
    """Базовый fallback для deterministic/tool узлов до внедрения реальной логики."""

    component_ref = getattr(node, "component_ref", "unknown")
    return {{"status": "stub", "component_ref": component_ref}}


def _validator_fallback(_state: RenderedGraphState, _node: Any) -> dict[str, Any]:
    """Fallback-валидатор: пропускает кейс, пока доменный валидатор не подключен."""

    return {{"valid": True}}


def _hitl_fallback(state: RenderedGraphState, _node: Any) -> dict[str, Any]:
    """Fallback для HITL: берет решение из payload или использует approve."""

    decision = state.payload.get("review_decision", "approve")
    return {{"review_decision": decision}}
'''

    def _render_agent_class(self) -> str:
        """Формирует основной класс `GeneratedAgent` для runtime-вызовов."""

        return '''"""Основной класс сгенерированного агента."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.renderer.langgraph_dai.adapter import GraphIRToLangGraphRenderer

from .bindings import build_bindings


class GeneratedAgent:
    """Исполняемый агент, собранный из сохраненного Graph IR."""

    def __init__(self) -> None:
        """Инициализирует runtime на основе `graph_ir.json` и сгенерированных биндингов."""

        graph_ir_path = Path(__file__).resolve().parent / "graph_ir.json"
        graph_ir = load_graph_ir_spec(graph_ir_path)
        renderer = GraphIRToLangGraphRenderer()
        self._runtime = renderer.render(graph_ir=graph_ir, bindings=build_bindings())

    def invoke(self, payload: dict[str, Any], *, task_id: str = "generated-task") -> dict[str, Any]:
        """Запускает агент и возвращает итоговое состояние в виде JSON-совместимого словаря."""

        final_state = self._runtime.invoke(payload=payload, task_id=task_id)
        return {
            "executed_nodes": final_state.executed_nodes,
            "skipped_nodes": final_state.skipped_nodes,
            "errors": final_state.errors,
            "payload": final_state.payload,
            "node_outputs": final_state.node_outputs,
            "trace": final_state.trace,
        }
'''

    def _render_entrypoint(self, package_name: str) -> str:
        """Формирует CLI-скрипт запуска сгенерированного агента."""

        return f'''"""CLI запуска сгенерированного агента."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

def _bootstrap_optimizer_import_path() -> None:
    """Добавляет путь к локальному `optimizer`, если сгенерированный код запущен из репозитория."""

    cwd = Path.cwd()
    if (cwd / "optimizer" / "__init__.py").exists():
        sys.path.insert(0, str(cwd))
        return

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "optimizer" / "__init__.py").exists():
            sys.path.insert(0, str(parent))
            return


_bootstrap_optimizer_import_path()

from {package_name}.agent import GeneratedAgent


def build_parser() -> argparse.ArgumentParser:
    """Создает парсер аргументов для запуска `GeneratedAgent`."""

    parser = argparse.ArgumentParser(description="Запуск сгенерированного агента AutoAgent Optimizer")
    parser.add_argument("--payload-json", default="{{}}", help="JSON-объект входного payload.")
    parser.add_argument("--payload-file", default="", help="Путь до JSON-файла payload.")
    parser.add_argument("--task-id", default="generated-task", help="task_id для runtime state.")
    parser.add_argument("--pretty", action="store_true", help="Печатать результат в pretty JSON.")
    return parser


def parse_payload(args: argparse.Namespace) -> dict[str, Any]:
    """Разрешает payload из файла или inline JSON-аргумента."""

    if args.payload_file:
        payload_text = Path(args.payload_file).resolve().read_text(encoding="utf-8-sig")
        payload = json.loads(payload_text)
    else:
        payload = json.loads(args.payload_json)
    if not isinstance(payload, dict):
        raise ValueError("payload должен быть JSON-объектом.")
    return payload


def main() -> None:
    """Точка входа CLI `python run_generated_agent.py`."""

    parser = build_parser()
    args = parser.parse_args()
    payload = parse_payload(args)
    agent = GeneratedAgent()
    result = agent.invoke(payload=payload, task_id=args.task_id)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
'''

    def _render_readme(self, package_name: str) -> str:
        """Формирует README для разработчика по использованию сгенерированного кода."""

        return f"""# Generated Agent Package

Этот каталог создан AutoAgent Optimizer как кодовый артефакт найденной конфигурации.

## Структура

- `{package_name}/graph_ir.json` — зафиксированный Graph IR.
- `{package_name}/bindings.py` — prompt templates и реестры обработчиков.
- `{package_name}/agent.py` — класс `GeneratedAgent` с методом `invoke`.
- `run_generated_agent.py` — CLI запуск агента.

## Запуск

```powershell
python .\\run_generated_agent.py --payload-json "{{\\"query\\": \\"Explain result\\"}}" --pretty
```

## Что нужно доработать вручную

1. Заполнить `prompt_templates` в `bindings.py`.
2. Заменить fallback-обработчики на реальные `python://` или registry-callables.
3. Для внешних `mcp://` инструментов подключить реальный runtime adapter.
"""


def sanitize_package_name(raw_name: str) -> str:
    """Нормализует имя Python-пакета для сгенерированного агента."""

    cleaned = []
    for ch in raw_name.strip().lower():
        if ch.isalnum() or ch == "_":
            cleaned.append(ch)
        elif ch in ("-", " ", "."):
            cleaned.append("_")
    value = "".join(cleaned).strip("_")
    if not value:
        value = "generated_agent"
    if value[0].isdigit():
        value = f"agent_{value}"
    return value


def _collect_prompt_ids(graph_ir: GraphIRSpec) -> set[str]:
    """Собирает set всех prompt_id из узлов Graph IR."""

    prompt_ids: set[str] = set()
    for node in graph_ir.nodes:
        prompt_id = node.config.get("prompt_id")
        if isinstance(prompt_id, str) and prompt_id.strip():
            prompt_ids.add(prompt_id.strip())
    return prompt_ids


def _collect_component_refs(graph_ir: GraphIRSpec, kind: GraphNodeKind) -> set[str]:
    """Собирает set component_ref для указанного типа узлов."""

    refs: set[str] = set()
    for node in graph_ir.nodes:
        if node.kind == kind and node.component_ref.strip():
            refs.add(node.component_ref.strip())
    return refs


def _render_registry_lines(component_refs: Iterable[str], fallback_name: str) -> str:
    """Рендерит строки dictionary-реестра с ленивым python resolver и fallback."""

    lines: list[str] = []
    for component_ref in component_refs:
        line = (
            f'        "{component_ref}": _resolve_python_callable_or_fallback('
            f'"{component_ref}", {fallback_name}),'
        )
        lines.append(line)
    if not lines:
        lines.append("        # Для этого типа узлов component_ref отсутствуют.")
    return "\n".join(lines)
