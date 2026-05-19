"""Preflight-проверка совместимости evaluation profile с native runtime target."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.evaluation.profile_schema import EvaluationProfileSpec
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.graph_ir.models import GraphIRSpec, GraphNodeKind

# Поддерживаемые node kinds в native exporter v0.
SUPPORTED_NATIVE_NODE_KINDS = {
    GraphNodeKind.LLM,
    GraphNodeKind.DETERMINISTIC,
    GraphNodeKind.VALIDATOR,
}


@dataclass(frozen=True)
class NativeCompatibilityIssue:
    """Описывает одну проблему совместимости participant-а с native runtime target."""

    node_id: str
    kind: str
    component_ref: str
    reason: str
    recommendation: str

    def to_payload(self) -> dict[str, str]:
        """Преобразует issue в JSON-совместимую структуру."""

        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "component_ref": self.component_ref,
            "reason": self.reason,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class NativeParticipantCompatibilityResult:
    """Результат preflight-проверки одного participant-а."""

    participant_id: str
    source_kind: str
    source_path: str
    compatible: bool
    issues: list[NativeCompatibilityIssue] = field(default_factory=list)
    message: str = ""

    def to_payload(self) -> dict[str, Any]:
        """Преобразует participant-level результат preflight в JSON."""

        return {
            "participant_id": self.participant_id,
            "source_kind": self.source_kind,
            "source_path": self.source_path,
            "compatible": self.compatible,
            "issues": [item.to_payload() for item in self.issues],
            "message": self.message,
        }


@dataclass(frozen=True)
class NativeCompatibilityPreflightReport:
    """Сводный preflight-отчет совместимости profile с native runtime target."""

    target: str
    mode: str
    profile_id: str
    participants_total: int
    compatible_total: int
    incompatible_total: int
    participants: list[NativeParticipantCompatibilityResult]

    @property
    def can_execute_native(self) -> bool:
        """Показывает, можно ли безопасно запускать native-runtime evaluation."""

        return self.incompatible_total == 0

    def to_payload(self) -> dict[str, Any]:
        """Преобразует preflight-отчет в JSON-совместимую структуру."""

        return {
            "target": self.target,
            "mode": self.mode,
            "profile_id": self.profile_id,
            "supported_node_kinds": sorted(item.value for item in SUPPORTED_NATIVE_NODE_KINDS),
            "participants_total": self.participants_total,
            "compatible_total": self.compatible_total,
            "incompatible_total": self.incompatible_total,
            "can_execute_native": self.can_execute_native,
            "participants": [item.to_payload() for item in self.participants],
        }


class NativeCompatibilityPreflightError(ValueError):
    """Ошибка preflight, блокирующая запуск native target при несовместимости профиля."""

    def __init__(self, *, report: NativeCompatibilityPreflightReport) -> None:
        """Инициализирует ошибку и сохраняет structured preflight report."""

        self.report = report
        super().__init__(
            "Native runtime preflight failed: профиль содержит participants с неподдержанными node kinds."
        )


def build_native_compatibility_preflight_report(
    *,
    profile: EvaluationProfileSpec,
    profile_file_dir: Path,
) -> NativeCompatibilityPreflightReport:
    """Собирает preflight-отчет совместимости profile для `native_runtime` target."""

    participant_results: list[NativeParticipantCompatibilityResult] = []
    for participant in profile.participants:
        source_kind, source_path = _participant_source(participant=participant, base_dir=profile_file_dir)
        try:
            graph_ir = _resolve_participant_graph_ir(participant=participant, base_dir=profile_file_dir)
        except (FileNotFoundError, ValueError) as exc:
            participant_results.append(
                NativeParticipantCompatibilityResult(
                    participant_id=participant.participant_id,
                    source_kind=source_kind,
                    source_path=source_path,
                    compatible=False,
                    issues=[
                        NativeCompatibilityIssue(
                            node_id="",
                            kind="graph_resolution",
                            component_ref="",
                            reason=str(exc),
                            recommendation=(
                                "Исправьте source-файл participant-а или временно исключите его из native profile."
                            ),
                        )
                    ],
                    message="Не удалось резолвить Graph IR participant-а для native preflight.",
                )
            )
            continue

        unsupported_nodes = [
            node for node in graph_ir.nodes if node.kind not in SUPPORTED_NATIVE_NODE_KINDS
        ]
        if not unsupported_nodes:
            participant_results.append(
                NativeParticipantCompatibilityResult(
                    participant_id=participant.participant_id,
                    source_kind=source_kind,
                    source_path=source_path,
                    compatible=True,
                    issues=[],
                    message="Participant совместим с native exporter v0.",
                )
            )
            continue

        issues = [
            NativeCompatibilityIssue(
                node_id=node.id,
                kind=node.kind.value,
                component_ref=node.component_ref,
                reason=f"Node kind `{node.kind.value}` не поддержан native exporter v0.",
                recommendation=(
                    "Удалите/замените узел для native target, запускайте этот participant на dsl_runtime "
                    "или дождитесь расширения поддержки native bindings (I4.S6+)."
                ),
            )
            for node in unsupported_nodes
        ]
        participant_results.append(
            NativeParticipantCompatibilityResult(
                participant_id=participant.participant_id,
                source_kind=source_kind,
                source_path=source_path,
                compatible=False,
                issues=issues,
                message="Participant несовместим с native exporter v0 из-за unsupported node kinds.",
            )
        )

    compatible_total = sum(1 for item in participant_results if item.compatible)
    incompatible_total = len(participant_results) - compatible_total
    return NativeCompatibilityPreflightReport(
        target="native_runtime",
        mode="strict_preflight_v0",
        profile_id=profile.profile_id,
        participants_total=len(participant_results),
        compatible_total=compatible_total,
        incompatible_total=incompatible_total,
        participants=participant_results,
    )


def _resolve_participant_graph_ir(*, participant: Any, base_dir: Path) -> GraphIRSpec:
    """Резолвит Graph IR participant-а напрямую или через компиляцию DSL."""

    if str(participant.graph_ir_file).strip():
        return load_graph_ir_spec(_resolve_path(base_dir, participant.graph_ir_file))

    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(_resolve_path(base_dir, participant.dsl_file))
    if compile_result.graph_ir is None:
        raise ValueError(
            f"Не удалось скомпилировать DSL участника `{participant.participant_id}`: {compile_result.report.summary()}"
        )
    return compile_result.graph_ir


def _participant_source(*, participant: Any, base_dir: Path) -> tuple[str, str]:
    """Возвращает source kind/path participant-а для preflight отчета."""

    if str(participant.graph_ir_file).strip():
        return "graph_ir", str(_resolve_path(base_dir, participant.graph_ir_file))
    return "dsl", str(_resolve_path(base_dir, participant.dsl_file))


def _resolve_path(base_dir: Path, path_value: str) -> Path:
    """Резолвит абсолютный путь или путь относительно директории profile."""

    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()
