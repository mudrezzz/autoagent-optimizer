"""Р­РєСЃРїРѕСЂС‚ standalone native-Р°РіРµРЅС‚Р° РЅР° `langgraph-dai` Р±РµР· runtime-Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ optimizer."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from optimizer.graph_ir.models import GraphIRSpec, GraphNodeKind


class NativeExportBuildError(ValueError):
    """РћС€РёР±РєР° РїРѕСЃС‚СЂРѕРµРЅРёСЏ standalone native export РїР°РєРµС‚Р°."""


@dataclass(frozen=True)
class NativeExportResult:
    """Р РµР·СѓР»СЊС‚Р°С‚ РіРµРЅРµСЂР°С†РёРё standalone native export РїР°РєРµС‚Р°."""

    output_dir: Path
    app_dir: Path
    run_file: Path
    workflow_file: Path
    prompts_file: Path
    graph_ir_file: Path
    requirements_file: Path
    readme_file: Path

    def to_payload(self) -> dict[str, str]:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ JSON-СЃРѕРІРјРµСЃС‚РёРјСѓСЋ СЃРІРѕРґРєСѓ РїРѕ СЃРѕР·РґР°РЅРЅС‹Рј Р°СЂС‚РµС„Р°РєС‚Р°Рј native export."""

        return {
            "output_dir": str(self.output_dir),
            "app_dir": str(self.app_dir),
            "run_file": str(self.run_file),
            "workflow_file": str(self.workflow_file),
            "prompts_file": str(self.prompts_file),
            "graph_ir_file": str(self.graph_ir_file),
            "requirements_file": str(self.requirements_file),
            "readme_file": str(self.readme_file),
        }


class NativeLanggraphDaiExporter:
    """Р“РµРЅРµСЂР°С‚РѕСЂ standalone native-Р°РіРµРЅС‚Р° РЅР° РєРѕРЅС‚СЂР°РєС‚Р°С… `framework`/`infra.openrouter`."""

    def export(
        self,
        *,
        graph_ir: GraphIRSpec,
        prompt_templates: dict[str, str],
        output_dir: Path,
        force: bool = False,
    ) -> NativeExportResult:
        """РЎРѕР·РґР°РµС‚ standalone native package РІ РєР°С‚Р°Р»РѕРіРµ `output_dir`."""

        _validate_graph_support(graph_ir)

        resolved_output_dir = output_dir.resolve()
        if resolved_output_dir.exists():
            if not force:
                raise NativeExportBuildError(
                    f"РљР°С‚Р°Р»РѕРі native export СѓР¶Рµ СЃСѓС‰РµСЃС‚РІСѓРµС‚: {resolved_output_dir}. РСЃРїРѕР»СЊР·СѓР№С‚Рµ force=true."
                )
            shutil.rmtree(resolved_output_dir)
        resolved_output_dir.mkdir(parents=True, exist_ok=True)

        app_dir = resolved_output_dir / "app"
        config_dir = resolved_output_dir / "config"
        prompts_dir = resolved_output_dir / "prompts"
        artifacts_dir = resolved_output_dir / "artifacts"
        app_dir.mkdir(parents=True, exist_ok=True)
        config_dir.mkdir(parents=True, exist_ok=True)
        prompts_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        _copy_python_dependency_files(graph_ir=graph_ir, native_root=resolved_output_dir)

        workflow_file = app_dir / "workflow.py"
        run_file = app_dir / "run.py"
        init_file = app_dir / "__init__.py"
        prompts_file = prompts_dir / "prompts.json"
        graph_ir_file = artifacts_dir / "source_graph_ir.json"
        config_file = config_dir / "workflow.json"
        requirements_file = resolved_output_dir / "requirements.txt"
        readme_file = resolved_output_dir / "README.md"

        init_file.write_text('"""Standalone native agent package."""\n', encoding="utf-8")
        workflow_file.write_text(_render_workflow_py(), encoding="utf-8")
        run_file.write_text(_render_run_py(), encoding="utf-8")
        prompts_file.write_text(json.dumps(prompt_templates, ensure_ascii=False, indent=2), encoding="utf-8")
        graph_ir_file.write_text(graph_ir.model_dump_json(indent=2), encoding="utf-8")
        config_file.write_text(
            json.dumps(
                {
                    "entrypoint": "app/run.py",
                    "graph_ir_file": "artifacts/source_graph_ir.json",
                    "prompts_file": "prompts/prompts.json",
                    "runtime_mode": "langgraph_dai_native_v0",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        requirements_file.write_text(
            "langgraph-dai @ git+https://github.com/mudrezzz/langgraph-document-ai-platform.git@main#subdirectory=backend/packages\n",
            encoding="utf-8",
        )
        readme_file.write_text(_render_readme(), encoding="utf-8")

        return NativeExportResult(
            output_dir=resolved_output_dir,
            app_dir=app_dir,
            run_file=run_file,
            workflow_file=workflow_file,
            prompts_file=prompts_file,
            graph_ir_file=graph_ir_file,
            requirements_file=requirements_file,
            readme_file=readme_file,
        )


def _validate_graph_support(graph_ir: GraphIRSpec) -> None:
    """РџСЂРѕРІРµСЂСЏРµС‚, С‡С‚Рѕ Graph IR РїРѕРґРґРµСЂР¶Р°РЅ minimal native export СЂРµР°Р»РёР·Р°С†РёРµР№."""

    supported_kinds = {
        GraphNodeKind.LLM,
        GraphNodeKind.DETERMINISTIC,
        GraphNodeKind.TOOL,
        GraphNodeKind.VALIDATOR,
        GraphNodeKind.HITL_GATE,
    }
    unsupported = sorted(node.id for node in graph_ir.nodes if node.kind not in supported_kinds)
    if unsupported:
        raise NativeExportBuildError(
            "Native export v0 РїРѕРґРґРµСЂР¶РёРІР°РµС‚ С‚РѕР»СЊРєРѕ llm/deterministic/tool/validator/hitl_gate. "
            f"РќРµРїРѕРґРґРµСЂР¶Р°РЅРЅС‹Рµ node ids: {', '.join(unsupported)}."
        )


def _copy_python_dependency_files(*, graph_ir: GraphIRSpec, native_root: Path) -> None:
    """РљРѕРїРёСЂСѓРµС‚ Р»РѕРєР°Р»СЊРЅС‹Рµ python-РјРѕРґСѓР»Рё РёР· `python://` refs РІ standalone native РїР°РєРµС‚."""

    project_root = Path(__file__).resolve().parents[2]
    modules: set[str] = set()
    for node in graph_ir.nodes:
        component_ref = node.component_ref.strip()
        if not component_ref.startswith("python://"):
            continue
        raw = component_ref[len("python://") :]
        if ":" not in raw:
            continue
        module_name, _func_name = raw.split(":", 1)
        module_name = module_name.strip()
        if module_name:
            modules.add(module_name)

    for module_name in sorted(modules):
        _copy_module_with_package_inits(project_root=project_root, native_root=native_root, module_name=module_name)

    # Р”Р»СЏ style-validator РєРµР№СЃР° РїРµСЂРµРЅРѕСЃРёРј СЂРµСЃСѓСЂСЃС‹ РїР°С‚С‚РµСЂРЅРѕРІ РІ standalone РїР°РєРµС‚.
    resources_src = project_root / "examples" / "resources" / "ai_style_patterns_ru_v1.json"
    if resources_src.exists():
        resources_dst = native_root / "examples" / "resources" / "ai_style_patterns_ru_v1.json"
        resources_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(resources_src, resources_dst)


def _copy_module_with_package_inits(*, project_root: Path, native_root: Path, module_name: str) -> None:
    """РљРѕРїРёСЂСѓРµС‚ РјРѕРґСѓР»СЊ Рё С†РµРїРѕС‡РєСѓ `__init__.py` РґР»СЏ РєРѕСЂСЂРµРєС‚РЅРѕРіРѕ РёРјРїРѕСЂС‚-СЂРµР·РѕР»РІР° РІ native РїР°РєРµС‚Рµ."""

    module_rel = Path(*module_name.split("."))
    module_py = project_root / module_rel.with_suffix(".py")
    package_dir = project_root / module_rel

    if module_py.exists():
        destination_py = native_root / module_rel.with_suffix(".py")
        destination_py.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(module_py, destination_py)
        _copy_package_init_chain(project_root=project_root, native_root=native_root, module_rel=module_rel)
        return

    if package_dir.is_dir():
        destination_dir = native_root / module_rel
        shutil.copytree(package_dir, destination_dir, dirs_exist_ok=True)
        _copy_package_init_chain(project_root=project_root, native_root=native_root, module_rel=module_rel)


def _copy_package_init_chain(*, project_root: Path, native_root: Path, module_rel: Path) -> None:
    """РљРѕРїРёСЂСѓРµС‚ `__init__.py` РґР»СЏ РєР°Р¶РґРѕРіРѕ СѓСЂРѕРІРЅСЏ package-chain РјРѕРґСѓР»СЏ."""

    parts = list(module_rel.parts)
    if not parts:
        return
    for depth in range(1, len(parts) + 1):
        rel_dir = Path(*parts[:depth])
        init_src = project_root / rel_dir / "__init__.py"
        if not init_src.exists():
            continue
        init_dst = native_root / rel_dir / "__init__.py"
        init_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(init_src, init_dst)


def _render_workflow_py() -> str:
    """Р¤РѕСЂРјРёСЂСѓРµС‚ `app/workflow.py` РґР»СЏ standalone native runtime."""

    return '''"""Standalone workflow runtime РґР»СЏ native `langgraph-dai` export v0."""

from __future__ import annotations

import importlib
import json
import os
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from types import SimpleNamespace

from framework.workflows.base import BaseWorkflow, WorkflowExecutionContext, WorkflowNodeSpec
from infra.openrouter.chat_gateway import OpenRouterChatModelGateway
from pydantic import BaseModel, Field


class NativeAgentState(BaseModel):
    """РўРёРї СЃРѕСЃС‚РѕСЏРЅРёСЏ standalone native workflow."""

    payload: dict[str, Any] = Field(default_factory=dict)
    task_context: dict[str, Any] = Field(default_factory=dict)
    active_nodes: list[str] = Field(default_factory=list)
    executed_nodes: list[str] = Field(default_factory=list)
    skipped_nodes: list[str] = Field(default_factory=list)
    node_outputs: dict[str, Any] = Field(default_factory=dict)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class NativeGraphConfig:
    """РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ standalone native workflow."""

    graph_ir: dict[str, Any]
    prompt_templates: dict[str, str]


class NativeGraphWorkflow(BaseWorkflow):
    """Workflow, РёСЃРїРѕР»РЅСЏСЋС‰РёР№ Graph IR РІ standalone native runtime-РєРѕРЅС‚СѓСЂРµ."""

    def __init__(self, config: NativeGraphConfig) -> None:
        """РРЅРёС†РёР°Р»РёР·РёСЂСѓРµС‚ workflow РёР· JSON-РєРѕРЅС„РёРіСѓСЂР°С†РёРё graph_ir Рё prompt templates."""

        self._graph_ir = config.graph_ir
        self._prompt_templates = config.prompt_templates
        self._llm_gateway = _build_openrouter_gateway_if_available()
        self._nodes_by_id = {str(node["id"]): node for node in self._graph_ir.get("nodes", []) if isinstance(node, dict)}
        self._edges_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for edge in self._graph_ir.get("edges", []):
            if isinstance(edge, dict):
                self._edges_by_source[str(edge.get("source", ""))].append(edge)
        self._topological_order = _build_topological_order(self._graph_ir)
        super().__init__(use_langgraph_runtime=True)
        self.compile()

    def state_schema(self) -> type[NativeAgentState]:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃС…РµРјСѓ СЃРѕСЃС‚РѕСЏРЅРёСЏ workflow."""

        return NativeAgentState

    def workflow_nodes(self, *, is_resume: bool):
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ node handlers РІ С‚РѕРїРѕР»РѕРіРёС‡РµСЃРєРѕРј РїРѕСЂСЏРґРєРµ."""

        _ = is_resume
        return [WorkflowNodeSpec(name=node_id, handler=self._build_node_handler(node_id)) for node_id in self._topological_order]

    def _build_node_handler(self, node_id: str):
        """РЎРѕР·РґР°РµС‚ РѕР±СЂР°Р±РѕС‚С‡РёРє РІС‹РїРѕР»РЅРµРЅРёСЏ РѕРґРЅРѕРіРѕ СѓР·Р»Р° Graph IR."""

        def _handler(state: NativeAgentState, context: WorkflowExecutionContext) -> NativeAgentState:
            _ = context
            return self._execute_graph_node(node_id=node_id, state=state)

        return _handler

    def _execute_graph_node(self, *, node_id: str, state: NativeAgentState) -> NativeAgentState:
        """РСЃРїРѕР»РЅСЏРµС‚ СѓР·РµР» РїРѕ active frontier Рё СЂР°СЃСЃС‡РёС‚С‹РІР°РµС‚ СЃР»РµРґСѓСЋС‰СѓСЋ РІРѕР»РЅСѓ Р°РєС‚РёРІРЅС‹С… СѓР·Р»РѕРІ."""

        active_set = set(state.active_nodes or [])
        if not active_set:
            entry_node = str(self._graph_ir.get("entry_node", ""))
            if entry_node:
                active_set.add(entry_node)

        if node_id not in active_set:
            skipped_nodes = list(state.skipped_nodes)
            skipped_nodes.append(node_id)
            trace = list(state.trace)
            trace.append({"node_id": node_id, "status": "skipped"})
            return state.model_copy(update={"skipped_nodes": skipped_nodes, "trace": trace})

        node = self._nodes_by_id[node_id]
        active_set.remove(node_id)
        payload = dict(state.payload)
        node_outputs = dict(state.node_outputs)
        errors = list(state.errors)
        trace = list(state.trace)

        try:
            output = self._execute_node_with_policy(node=node, payload=payload, node_outputs=node_outputs)
            node_outputs[node_id] = output
            if isinstance(output, dict):
                payload.update(output)
            status = "completed"
        except Exception as exc:
            errors.append(f"{node_id}: {exc}")
            status = "failed"
            on_fail = str(node.get("on_fail", "stop"))
            if on_fail == "fallback":
                fallback_output = {"status": "fallback", "error": str(exc)}
                node_outputs[node_id] = fallback_output
                payload.update(fallback_output)
                status = "fallback"
            else:
                trace.append({"node_id": node_id, "status": status, "error": str(exc)})
                raise

        next_nodes = self._resolve_next_nodes(
            node_id=node_id,
            payload=payload,
            node_outputs=node_outputs,
            task_context=state.task_context,
        )
        active_set.update(next_nodes)

        executed_nodes = list(state.executed_nodes)
        executed_nodes.append(node_id)
        trace.append({"node_id": node_id, "status": status, "next_nodes": sorted(next_nodes)})
        return state.model_copy(
            update={
                "payload": payload,
                "active_nodes": sorted(active_set),
                "executed_nodes": executed_nodes,
                "node_outputs": node_outputs,
                "errors": errors,
                "trace": trace,
            }
        )

    def _resolve_next_nodes(
        self,
        *,
        node_id: str,
        payload: dict[str, Any],
        node_outputs: dict[str, Any],
        task_context: dict[str, Any],
    ) -> set[str]:
        """Р РµР·РѕР»РІРёС‚ СЃР»РµРґСѓСЋС‰РёРµ СѓР·Р»С‹ РїРѕ edge-СѓСЃР»РѕРІРёСЏРј."""

        next_nodes: set[str] = set()
        for edge in self._edges_by_source.get(node_id, []):
            condition = edge.get("condition")
            if _evaluate_condition(condition=condition, payload=payload, node_outputs=node_outputs, task_context=task_context):
                target = str(edge.get("target", "")).strip()
                if target:
                    next_nodes.add(target)
        return next_nodes

    def _execute_node_with_policy(
        self,
        *,
        node: dict[str, Any],
        payload: dict[str, Any],
        node_outputs: dict[str, Any],
    ) -> Any:
        """РСЃРїРѕР»РЅСЏРµС‚ СѓР·РµР» СЃ СѓС‡РµС‚РѕРј РїРѕР»РёС‚РёРєРё `on_fail`."""

        on_fail = str(node.get("on_fail", "stop"))
        if on_fail != "retry":
            return self._execute_node(node=node, payload=payload, node_outputs=node_outputs)

        first_error: Exception | None = None
        for _attempt in (1, 2):
            try:
                return self._execute_node(node=node, payload=payload, node_outputs=node_outputs)
            except Exception as exc:
                if first_error is None:
                    first_error = exc
        assert first_error is not None
        raise first_error

    def _execute_node(self, *, node: dict[str, Any], payload: dict[str, Any], node_outputs: dict[str, Any]) -> Any:
        """РСЃРїРѕР»РЅСЏРµС‚ node kind РІ minimal native runtime РєРѕРЅС‚СЂР°РєС‚Рµ."""

        kind = str(node.get("kind", "")).strip()
        if kind == "llm":
            return self._execute_llm(node=node, payload=payload)
        if kind == "deterministic":
            return self._execute_deterministic(node=node, payload=payload)
        if kind == "tool":
            return self._execute_tool(node=node, payload=payload)
        if kind == "validator":
            return self._execute_validator(node=node, payload=payload, node_outputs=node_outputs)
        if kind == "hitl_gate":
            return self._execute_hitl_gate(node=node, payload=payload)
        raise NotImplementedError(f"Node kind `{kind}` РЅРµ РїРѕРґРґРµСЂР¶Р°РЅ РІ native export v0.")

    def _execute_llm(self, *, node: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """РСЃРїРѕР»РЅСЏРµС‚ LLM СѓР·РµР» СЃ prompt templates Рё OpenRouter gateway."""

        prompt_id = ""
        node_config = node.get("config")
        if isinstance(node_config, dict):
            prompt_id = str(node_config.get("prompt_id", "")).strip()
        template = self._prompt_templates.get(prompt_id, "")
        if template:
            prompt = template.format_map(_SafeDict(payload))
        else:
            prompt = str(payload.get("query", payload))

        if self._llm_gateway is None:
            return {"text": f"[mock-llm] {prompt}"}
        response_text = self._llm_gateway.generate(prompt, metadata={"temperature": 0.2})
        return {"text": response_text}

    def _execute_deterministic(self, *, node: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """РСЃРїРѕР»РЅСЏРµС‚ deterministic СѓР·РµР» С‡РµСЂРµР· python:// callable РёР»Рё fallback stub."""

        component_ref = str(node.get("component_ref", "")).strip()
        if component_ref.startswith("python://"):
            try:
                callable_obj = _load_python_callable(component_ref)
                state_proxy = _build_state_proxy(payload)
                result = _invoke_python_callable(callable_obj, state_proxy, node)
                if isinstance(result, dict):
                    return result
                return {"deterministic_result": result}
            except Exception as exc:
                return {
                    "status": "deterministic_stub",
                    "component_ref": component_ref,
                    "reason": "python_callable_unresolved",
                    "error": str(exc),
                }
        return {"status": "deterministic_stub", "component_ref": component_ref}

    def _execute_tool(self, *, node: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """РСЃРїРѕР»РЅСЏРµС‚ tool-СѓР·РµР» РІ native runtime СЃ СЏРІРЅС‹Рј РєРѕРЅС‚СЂР°РєС‚РѕРј РґР»СЏ python:// Рё mcp:// refs."""

        component_ref = str(node.get("component_ref", "")).strip()
        if component_ref.startswith("python://"):
            callable_obj = _load_python_callable(component_ref)
            state_proxy = _build_state_proxy(payload)
            result = _invoke_python_callable(callable_obj, state_proxy, node)
            if isinstance(result, dict):
                return result
            return {"tool_result": result}

        if component_ref.startswith("mcp://"):
            # Р”Рѕ РїРѕР»РЅРѕР№ MCP РёРЅС‚РµРіСЂР°С†РёРё РІ native runtime v0 РґРµР»Р°РµРј СЏРІРЅС‹Р№ stub, С‡С‚РѕР±С‹
            # РїРѕРІРµРґРµРЅРёРµ Р±С‹Р»Рѕ РЅР°Р±Р»СЋРґР°РµРјС‹Рј Рё РґРёР°РіРЅРѕСЃС‚РёСЂСѓРµРјС‹Рј РІ trace/node_outputs.
            return {"status": "mcp_stub", "component_ref": component_ref}

        raise RuntimeError(f"РќРµ РЅР°Р№РґРµРЅ native tool binding РґР»СЏ component_ref: {component_ref}")

    def _execute_validator(
        self,
        *,
        node: dict[str, Any],
        payload: dict[str, Any],
        node_outputs: dict[str, Any],
    ) -> dict[str, Any]:
        """РСЃРїРѕР»РЅСЏРµС‚ validator СѓР·РµР» Рё РЅРѕСЂРјР°Р»РёР·СѓРµС‚ valid-СЂРµР·СѓР»СЊС‚Р°С‚."""

        component_ref = str(node.get("component_ref", "")).strip()
        if component_ref.startswith("python://"):
            try:
                callable_obj = _load_python_callable(component_ref)
                state_proxy = _build_state_proxy(payload)
                result = _invoke_python_callable(callable_obj, state_proxy, node)
            except Exception as exc:
                return {
                    "valid": True,
                    "status": "validator_stub",
                    "component_ref": component_ref,
                    "reason": "python_callable_unresolved",
                    "error": str(exc),
                }
        else:
            result = {"valid": True}

        if isinstance(result, bool):
            if not result:
                raise ValueError(f"Validator `{component_ref}` РІРµСЂРЅСѓР» False")
            return {"valid": True}
        if isinstance(result, dict):
            if result.get("valid") is False:
                raise ValueError(f"Validator `{component_ref}` РІРµСЂРЅСѓР» valid=False")
            return result
        return {"valid": True, "raw": result}

    def _execute_hitl_gate(self, *, node: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """РСЃРїРѕР»РЅСЏРµС‚ HITL gate СѓР·РµР» РІ native runtime СЃ РґРµС„РѕР»С‚РЅРѕР№ approve-СЃРµРјР°РЅС‚РёРєРѕР№."""

        component_ref = str(node.get("component_ref", "")).strip()
        if component_ref.startswith("python://"):
            try:
                callable_obj = _load_python_callable(component_ref)
                state_proxy = _build_state_proxy(payload)
                result = _invoke_python_callable(callable_obj, state_proxy, node)
                if isinstance(result, dict):
                    return result
                return {"review_decision": str(result)}
            except Exception as exc:
                return {
                    "review_decision": str(payload.get("review_decision", "approve")),
                    "status": "hitl_stub",
                    "component_ref": component_ref,
                    "reason": "python_callable_unresolved",
                    "error": str(exc),
                }

        # Р”Р»СЏ workflow:// Рё РїСЂРѕС‡РёС… refs РїСЂРёРјРµРЅСЏРµРј С‚РѕС‚ Р¶Рµ fallback-РєРѕРЅС‚СЂР°РєС‚, С‡С‚Рѕ Рё РІ DSL runtime:
        # Р±РµСЂРµРј `review_decision` РёР· payload (РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ `approve`), С‡С‚РѕР±С‹ edge-СѓСЃР»РѕРІРёСЏ Р±С‹Р»Рё СЌРєРІРёРІР°Р»РµРЅС‚РЅС‹.
        return {"review_decision": str(payload.get("review_decision", "approve"))}


class _SafeDict(dict):
    """Р‘РµР·РѕРїР°СЃРЅС‹Р№ dict РґР»СЏ prompt.format_map СЃ placeholder fallback."""

    def __missing__(self, key: str) -> str:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ `{key}`, РµСЃР»Рё РєР»СЋС‡ РЅРµ РЅР°Р№РґРµРЅ РІ payload."""

        return "{" + key + "}"


def load_native_workflow(*, graph_ir_file: Path, prompts_file: Path) -> NativeGraphWorkflow:
    """Р—Р°РіСЂСѓР¶Р°РµС‚ standalone workflow РёР· С„Р°Р№Р»РѕРІ graph_ir/prompts."""

    graph_payload = json.loads(graph_ir_file.read_text(encoding="utf-8"))
    prompts_payload = json.loads(prompts_file.read_text(encoding="utf-8"))
    if not isinstance(graph_payload, dict):
        raise ValueError("graph_ir file РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ JSON-РѕР±СЉРµРєС‚РѕРј")
    if not isinstance(prompts_payload, dict):
        raise ValueError("prompts file РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ JSON-РѕР±СЉРµРєС‚РѕРј")
    return NativeGraphWorkflow(
        NativeGraphConfig(
            graph_ir=graph_payload,
            prompt_templates={str(key): str(value) for key, value in prompts_payload.items()},
        )
    )


def _build_topological_order(graph_payload: dict[str, Any]) -> list[str]:
    """РЎС‚СЂРѕРёС‚ С‚РѕРїРѕР»РѕРіРёС‡РµСЃРєРёР№ РїРѕСЂСЏРґРѕРє СѓР·Р»РѕРІ Рё РІР°Р»РёРґРёСЂСѓРµС‚ РѕС‚СЃСѓС‚СЃС‚РІРёРµ С†РёРєР»РѕРІ."""

    nodes = graph_payload.get("nodes", [])
    edges = graph_payload.get("edges", [])
    node_ids = [str(item.get("id", "")) for item in nodes if isinstance(item, dict)]
    incoming_count: dict[str, int] = {node_id: 0 for node_id in node_ids}
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("source", "")).strip()
        target = str(edge.get("target", "")).strip()
        if source in incoming_count and target in incoming_count:
            incoming_count[target] += 1
            adjacency[source].append(target)

    queue: deque[str] = deque(sorted([node_id for node_id, count in incoming_count.items() if count == 0]))
    order: list[str] = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for nxt in adjacency.get(current, []):
            incoming_count[nxt] -= 1
            if incoming_count[nxt] == 0:
                queue.append(nxt)

    if len(order) != len(node_ids):
        raise ValueError("Graph IR СЃРѕРґРµСЂР¶РёС‚ С†РёРєР»; native export v0 РЅРµ РїРѕРґРґРµСЂР¶РёРІР°РµС‚ С†РёРєР»РёС‡РµСЃРєРёРµ РіСЂР°С„С‹.")
    return order


def _evaluate_condition(
    *,
    condition: Any,
    payload: dict[str, Any],
    node_outputs: dict[str, Any],
    task_context: dict[str, Any],
) -> bool:
    """РћС†РµРЅРёРІР°РµС‚ СѓСЃР»РѕРІРёРµ edge (`==` / `!=`) РІ РјРёРЅРёРјР°Р»СЊРЅРѕРј РєРѕРЅС‚СЂР°РєС‚Рµ native export v0."""

    if condition is None:
        return True
    expression = str(condition).strip()
    if not expression:
        return True

    if "==" in expression:
        left, right = expression.split("==", 1)
        left_value = _resolve_variable(left.strip(), payload=payload, node_outputs=node_outputs, task_context=task_context)
        right_value = _parse_literal(right.strip())
        return left_value == right_value

    if "!=" in expression:
        left, right = expression.split("!=", 1)
        left_value = _resolve_variable(left.strip(), payload=payload, node_outputs=node_outputs, task_context=task_context)
        right_value = _parse_literal(right.strip())
        return left_value != right_value

    return False


def _resolve_variable(
    key: str,
    *,
    payload: dict[str, Any],
    node_outputs: dict[str, Any],
    task_context: dict[str, Any],
) -> Any:
    """Р РµР·РѕР»РІРёС‚ Р·РЅР°С‡РµРЅРёРµ РїРµСЂРµРјРµРЅРЅРѕР№ РёР· payload/task_context/node_outputs."""

    if key in payload:
        return payload[key]
    if key in task_context:
        return task_context[key]
    if key in node_outputs:
        return node_outputs[key]
    return None


def _parse_literal(raw: str) -> Any:
    """РџР°СЂСЃРёС‚ СЃС‚СЂРѕРєРѕРІС‹Р№ Р»РёС‚РµСЂР°Р» СѓСЃР»РѕРІРёСЏ РІ python-РїСЂРёРјРёС‚РёРІ."""

    value = raw.strip()
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1]
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _load_python_callable(component_ref: str):
    """Р—Р°РіСЂСѓР¶Р°РµС‚ python callable РёР· ref `python://module:function`."""

    raw = component_ref[len("python://") :]
    if ":" not in raw:
        raise ValueError(f"РќРµРєРѕСЂСЂРµРєС‚РЅС‹Р№ python component_ref: {component_ref}")
    module_name, func_name = raw.split(":", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name, None)
    if not callable(func):
        raise ValueError(f"Р¤СѓРЅРєС†РёСЏ `{func_name}` РЅРµ РЅР°Р№РґРµРЅР° РІ РјРѕРґСѓР»Рµ `{module_name}`.")
    return func


def _build_state_proxy(payload: dict[str, Any]) -> Any:
    """РЎС‚СЂРѕРёС‚ Р»РµРіРєРѕРІРµСЃРЅС‹Р№ state-like РѕР±СЉРµРєС‚ РґР»СЏ python callable РєРѕРЅС‚СЂР°РєС‚РѕРІ."""

    return SimpleNamespace(payload=payload)


def _invoke_python_callable(callable_obj: Any, state_proxy: Any, node: dict[str, Any]) -> Any:
    """Р’С‹Р·С‹РІР°РµС‚ python callable, РїРѕРґРґРµСЂР¶РёРІР°СЏ СЃРёРіРЅР°С‚СѓСЂС‹ `(state,node)` Рё `(payload)`."""

    try:
        return callable_obj(state_proxy, node)
    except TypeError:
        return callable_obj(state_proxy.payload)


def _build_openrouter_gateway_if_available() -> OpenRouterChatModelGateway | None:
    """РЎРѕР·РґР°РµС‚ OpenRouter gateway, РµСЃР»Рё API РєР»СЋС‡ РґРѕСЃС‚СѓРїРµРЅ РІ РѕРєСЂСѓР¶РµРЅРёРё."""

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None
    model_name = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct").strip() or "meta-llama/llama-3.1-8b-instruct"
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip() or "https://openrouter.ai/api/v1"
    return OpenRouterChatModelGateway(api_key=api_key, model_name=model_name, base_url=base_url)
'''


def _render_run_py() -> str:
    """Р¤РѕСЂРјРёСЂСѓРµС‚ `app/run.py` РґР»СЏ standalone Р·Р°РїСѓСЃРєР° native workflow."""

    return '''"""CLI Р·Р°РїСѓСЃРєР° standalone native `langgraph-dai` Р°РіРµРЅС‚Р°."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _bootstrap_import_path() -> None:
    """Р”РѕР±Р°РІР»СЏРµС‚ РєРѕСЂРµРЅСЊ native package РІ `sys.path` РґР»СЏ СЃС‚Р°Р±РёР»СЊРЅРѕРіРѕ РёРјРїРѕСЂС‚Р° `app.*`."""

    current = Path(__file__).resolve()
    root = current.parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_bootstrap_import_path()

from app.workflow import NativeAgentState, load_native_workflow


def build_parser() -> argparse.ArgumentParser:
    """РЎРѕР·РґР°РµС‚ CLI-РїР°СЂСЃРµСЂ Р°СЂРіСѓРјРµРЅС‚РѕРІ standalone Р·Р°РїСѓСЃРєР°."""

    parser = argparse.ArgumentParser(description="Run standalone native langgraph-dai agent")
    parser.add_argument("--payload-json", default="{}", help="JSON-РѕР±СЉРµРєС‚ РІС…РѕРґРЅРѕРіРѕ payload")
    parser.add_argument("--payload-file", default="", help="РџСѓС‚СЊ РґРѕ JSON-С„Р°Р№Р»Р° payload")
    parser.add_argument("--task-id", default="native-task", help="task_id РґР»СЏ task_context")
    parser.add_argument("--pretty", action="store_true", help="Р’С‹РІРµСЃС‚Рё pretty JSON")
    return parser


def _parse_payload(args: argparse.Namespace) -> dict[str, Any]:
    """Р Р°Р·СЂРµС€Р°РµС‚ payload РёР· С„Р°Р№Р»Р° РёР»Рё inline JSON-Р°СЂРіСѓРјРµРЅС‚Р°."""

    if args.payload_file:
        payload_raw = Path(args.payload_file).resolve().read_text(encoding="utf-8-sig")
        payload = json.loads(payload_raw)
    else:
        payload = json.loads(args.payload_json)
    if not isinstance(payload, dict):
        raise ValueError("payload РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ JSON-РѕР±СЉРµРєС‚РѕРј")
    return payload


def main() -> None:
    """Р—Р°РїСѓСЃРєР°РµС‚ standalone native workflow Рё РїРµС‡Р°С‚Р°РµС‚ РёС‚РѕРіРѕРІРѕРµ СЃРѕСЃС‚РѕСЏРЅРёРµ."""

    parser = build_parser()
    args = parser.parse_args()
    payload = _parse_payload(args)

    root_dir = Path(__file__).resolve().parents[1]
    workflow = load_native_workflow(
        graph_ir_file=root_dir / "artifacts" / "source_graph_ir.json",
        prompts_file=root_dir / "prompts" / "prompts.json",
    )
    initial = NativeAgentState(payload=payload, task_context={"task_id": args.task_id})
    result = workflow.invoke(initial)

    output = {
        "task_id": result.task_context.get("task_id"),
        "executed_nodes": result.executed_nodes,
        "skipped_nodes": result.skipped_nodes,
        "errors": result.errors,
        "payload": result.payload,
        "node_outputs": result.node_outputs,
        "trace": result.trace,
    }
    if args.pretty:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
'''


def _render_readme() -> str:
    """Р¤РѕСЂРјРёСЂСѓРµС‚ README РґР»СЏ standalone native export РїР°РєРµС‚Р°."""

    return """# Native Agent Export (langgraph-dai)

Р­С‚РѕС‚ РїР°РєРµС‚ СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅ AutoAgent Optimizer РєР°Рє standalone runtime artifact.

## РћСЃРѕР±РµРЅРЅРѕСЃС‚Рё v0

1. РќРµ СЃРѕРґРµСЂР¶РёС‚ РёРјРїРѕСЂС‚РѕРІ `optimizer.*`.
2. Р’С‹РїРѕР»РЅСЏРµС‚СЃСЏ РЅР° `framework`/`infra.openrouter` РєРѕРЅС‚СЂР°РєС‚Р°С… `langgraph-dai`.
3. РџРѕРґРґРµСЂР¶РёРІР°РµС‚ node kinds:
   - `llm`
   - `deterministic`
   - `tool`
   - `validator`
   - `hitl_gate`

## РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№

```powershell
python -m pip install -r .\\requirements.txt
```

## Р—Р°РїСѓСЃРє

```powershell
'{"draft_post":"Р’ СЌС‚РѕРј РїРѕСЃС‚Рµ РјРЅРѕРіРѕ AI-С€С‚Р°РјРїРѕРІ. РќСѓР¶РЅР° Р¶РёРІР°СЏ СЂРµРґР°РєС‚СѓСЂР° Р±РµР· РїРѕС‚РµСЂРё С„Р°РєС‚РѕРІ."}' | Set-Content -LiteralPath .\\payload.json -Encoding UTF8
python .\\app\\run.py --payload-file .\\payload.json --pretty
```

"""

