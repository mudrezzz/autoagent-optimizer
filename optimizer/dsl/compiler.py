"""Компилятор DSL v0 в runtime-neutral Graph IR v0."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from optimizer.dsl.compile_report import CompileStatus, DslCompileReport, NodeMappingRecord
from optimizer.dsl.io import DslLoadError, DslValidationError, load_dsl_spec
from optimizer.dsl.schema import AutoAgentDslSpec
from optimizer.graph_ir.models import GraphIREdge, GraphIRNode, GraphIRSpec, GraphNodeKind


@dataclass(frozen=True)
class DslCompileResult:
    """Результат компиляции DSL в Graph IR вместе с отчетом."""

    graph_ir: GraphIRSpec | None
    report: DslCompileReport


class DslToGraphIRCompiler:
    """Компонент компиляции DSL-спецификации в Graph IR."""

    def compile_spec(self, spec: AutoAgentDslSpec, *, source: str = "<in-memory>") -> DslCompileResult:
        """Компилирует уже валидированную DSL-спецификацию в Graph IR."""

        report = DslCompileReport(status=CompileStatus.SUCCESS, source=source)

        component_refs = {component.id: component.implementation for component in spec.components}
        ir_nodes: list[GraphIRNode] = []

        for dsl_node in spec.graph.nodes:
            component_ref = component_refs[dsl_node.component_id]
            ir_node = GraphIRNode(
                id=dsl_node.id,
                kind=GraphNodeKind(dsl_node.type.value),
                component_ref=component_ref,
                config={
                    "component_id": dsl_node.component_id,
                    "prompt_id": dsl_node.prompt_id,
                },
                on_fail=dsl_node.on_fail,
            )
            ir_nodes.append(ir_node)
            report.node_mappings.append(
                NodeMappingRecord(
                    dsl_node_id=dsl_node.id,
                    ir_node_id=ir_node.id,
                    dsl_type=dsl_node.type.value,
                    ir_kind=ir_node.kind.value,
                    component_id=dsl_node.component_id,
                    component_ref=component_ref,
                )
            )
            if dsl_node.type.value == "llm" and not dsl_node.prompt_id:
                report.add_warning(
                    "LLM узел не содержит `prompt_id`.",
                    context={"node_id": dsl_node.id},
                )

        ir_edges = [
            GraphIREdge(
                source=edge.source,
                target=edge.target,
                condition=edge.condition,
                label="conditional" if edge.condition else "main_flow",
            )
            for edge in spec.graph.edges
        ]

        terminal_nodes = _derive_terminal_nodes(spec=spec)
        graph_ir = GraphIRSpec(
            ir_version="0.1",
            entry_node=spec.graph.entry_node,
            terminal_nodes=terminal_nodes,
            nodes=ir_nodes,
            edges=ir_edges,
            metadata={
                "source_project_id": spec.project.id,
                "source_schema_version": spec.schema_version,
            },
        )
        return DslCompileResult(graph_ir=graph_ir, report=report)

    def compile_file(self, file_path: Path) -> DslCompileResult:
        """Компилирует DSL-файл и возвращает IR + отчет (или ошибку в отчете)."""

        source = str(file_path.resolve())
        try:
            spec = load_dsl_spec(file_path)
        except (DslLoadError, DslValidationError) as exc:
            report = DslCompileReport(status=CompileStatus.FAILURE, source=source)
            report.add_error(str(exc))
            return DslCompileResult(graph_ir=None, report=report)

        try:
            return self.compile_spec(spec, source=source)
        except Exception as exc:
            report = DslCompileReport(status=CompileStatus.FAILURE, source=source)
            report.add_error(str(exc))
            return DslCompileResult(graph_ir=None, report=report)


def _derive_terminal_nodes(spec: AutoAgentDslSpec) -> list[str]:
    """Определяет терминальные узлы как узлы без исходящих ребер."""

    outgoing_sources = {edge.source for edge in spec.graph.edges}
    terminal_nodes = [node.id for node in spec.graph.nodes if node.id not in outgoing_sources]
    return terminal_nodes

