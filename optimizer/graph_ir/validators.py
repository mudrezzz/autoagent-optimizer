"""Валидаторы целостности Graph IR."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from optimizer.graph_ir.models import GraphIREdge, GraphIRSpec


@dataclass(frozen=True)
class GraphIRValidationError(ValueError):
    """Ошибка проверки целостности Graph IR."""

    message: str

    def __str__(self) -> str:
        """Возвращает человекочитаемый текст ошибки."""

        return self.message


def validate_graph_ir(spec: "GraphIRSpec") -> None:
    """Проверяет структуру графа: start/end, ребра и достижимость узлов."""

    node_ids = [node.id for node in spec.nodes]
    node_set = set(node_ids)

    _validate_unique_nodes(node_ids)
    _validate_entry_node(spec.entry_node, node_set)
    _validate_terminal_nodes(spec.terminal_nodes, node_set)
    _validate_edge_endpoints(spec.edges, node_set)
    outgoing = _build_outgoing_map(spec.edges)
    _validate_non_terminal_outgoing(spec, outgoing)
    _validate_terminal_outgoing(spec, outgoing)
    reachable_nodes = _compute_reachable_nodes(spec.entry_node, outgoing)
    _validate_unreachable_nodes(node_set, reachable_nodes)
    _validate_terminal_reachability(spec.terminal_nodes, reachable_nodes)


def _validate_unique_nodes(node_ids: list[str]) -> None:
    """Проверяет уникальность идентификаторов узлов."""

    if len(node_ids) != len(set(node_ids)):
        raise GraphIRValidationError("Graph IR содержит дублирующиеся `nodes[].id`.")


def _validate_entry_node(entry_node: str, node_set: set[str]) -> None:
    """Проверяет существование стартового узла."""

    if entry_node not in node_set:
        raise GraphIRValidationError("`entry_node` отсутствует в списке узлов.")


def _validate_terminal_nodes(terminal_nodes: list[str], node_set: set[str]) -> None:
    """Проверяет корректность списка завершающих узлов."""

    if len(terminal_nodes) != len(set(terminal_nodes)):
        raise GraphIRValidationError("`terminal_nodes` содержит дубли.")
    missing = sorted(set(terminal_nodes) - node_set)
    if missing:
        raise GraphIRValidationError(f"`terminal_nodes` ссылается на отсутствующие узлы: {', '.join(missing)}.")


def _validate_edge_endpoints(edges: list["GraphIREdge"], node_set: set[str]) -> None:
    """Проверяет, что каждое ребро указывает на существующие узлы."""

    for edge in edges:
        if edge.source not in node_set:
            raise GraphIRValidationError(f"Источник ребра `{edge.source}` отсутствует среди узлов.")
        if edge.target not in node_set:
            raise GraphIRValidationError(f"Целевой узел ребра `{edge.target}` отсутствует среди узлов.")


def _build_outgoing_map(edges: list["GraphIREdge"]) -> dict[str, set[str]]:
    """Строит индекс исходящих ребер для каждого узла."""

    outgoing: dict[str, set[str]] = {}
    for edge in edges:
        outgoing.setdefault(edge.source, set()).add(edge.target)
    return outgoing


def _validate_non_terminal_outgoing(spec: "GraphIRSpec", outgoing: dict[str, set[str]]) -> None:
    """Проверяет, что у не-терминальных узлов есть хотя бы одно исходящее ребро."""

    terminal_set = set(spec.terminal_nodes)
    for node in spec.nodes:
        if node.id in terminal_set:
            continue
        if len(outgoing.get(node.id, set())) == 0:
            raise GraphIRValidationError(f"Не-терминальный узел `{node.id}` не имеет исходящих ребер.")


def _validate_terminal_outgoing(spec: "GraphIRSpec", outgoing: dict[str, set[str]]) -> None:
    """Проверяет, что терминальные узлы не имеют исходящих ребер."""

    for terminal in spec.terminal_nodes:
        if len(outgoing.get(terminal, set())) > 0:
            raise GraphIRValidationError(f"Терминальный узел `{terminal}` не должен иметь исходящие ребра.")


def _compute_reachable_nodes(entry_node: str, outgoing: dict[str, set[str]]) -> set[str]:
    """Вычисляет множество достижимых узлов BFS-обходом от `entry_node`."""

    visited: set[str] = set()
    queue: deque[str] = deque([entry_node])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for nxt in outgoing.get(current, set()):
            if nxt not in visited:
                queue.append(nxt)
    return visited


def _validate_unreachable_nodes(node_set: set[str], reachable_nodes: set[str]) -> None:
    """Проверяет отсутствие недостижимых узлов относительно `entry_node`."""

    unreachable = sorted(node_set - reachable_nodes)
    if unreachable:
        raise GraphIRValidationError(f"Обнаружены unreachable nodes: {', '.join(unreachable)}.")


def _validate_terminal_reachability(terminal_nodes: list[str], reachable_nodes: set[str]) -> None:
    """Проверяет достижимость всех терминальных узлов."""

    not_reachable = sorted(set(terminal_nodes) - reachable_nodes)
    if not_reachable:
        raise GraphIRValidationError(
            f"Терминальные узлы недостижимы от `entry_node`: {', '.join(not_reachable)}."
        )

