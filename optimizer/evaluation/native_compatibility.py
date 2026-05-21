"""Preflight-РїСЂРѕРІРµСЂРєР° СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё evaluation profile СЃ native runtime target."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from optimizer.dsl.compiler import DslToGraphIRCompiler
from optimizer.evaluation.profile_schema import EvaluationProfileSpec
from optimizer.graph_ir.io import load_graph_ir_spec
from optimizer.graph_ir.models import GraphIRSpec, GraphNodeKind

# РџРѕРґРґРµСЂР¶РёРІР°РµРјС‹Рµ node kinds РІ native exporter v0.
SUPPORTED_NATIVE_NODE_KINDS = {
    GraphNodeKind.LLM,
    GraphNodeKind.DETERMINISTIC,
    GraphNodeKind.TOOL,
    GraphNodeKind.VALIDATOR,
    GraphNodeKind.HITL_GATE,
}


@dataclass(frozen=True)
class NativeCompatibilityIssue:
    """РћРїРёСЃС‹РІР°РµС‚ РѕРґРЅСѓ РїСЂРѕР±Р»РµРјСѓ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё participant-Р° СЃ native runtime target."""

    node_id: str
    kind: str
    component_ref: str
    reason: str
    recommendation: str

    def to_payload(self) -> dict[str, str]:
        """РџСЂРµРѕР±СЂР°Р·СѓРµС‚ issue РІ JSON-СЃРѕРІРјРµСЃС‚РёРјСѓСЋ СЃС‚СЂСѓРєС‚СѓСЂСѓ."""

        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "component_ref": self.component_ref,
            "reason": self.reason,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class NativeParticipantCompatibilityResult:
    """Р РµР·СѓР»СЊС‚Р°С‚ preflight-РїСЂРѕРІРµСЂРєРё РѕРґРЅРѕРіРѕ participant-Р°."""

    participant_id: str
    source_kind: str
    source_path: str
    compatible: bool
    issues: list[NativeCompatibilityIssue] = field(default_factory=list)
    message: str = ""

    def to_payload(self) -> dict[str, Any]:
        """РџСЂРµРѕР±СЂР°Р·СѓРµС‚ participant-level СЂРµР·СѓР»СЊС‚Р°С‚ preflight РІ JSON."""

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
    """РЎРІРѕРґРЅС‹Р№ preflight-РѕС‚С‡РµС‚ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё profile СЃ native runtime target."""

    target: str
    mode: str
    profile_id: str
    participants_total: int
    compatible_total: int
    incompatible_total: int
    participants: list[NativeParticipantCompatibilityResult]

    @property
    def can_execute_native(self) -> bool:
        """РџРѕРєР°Р·С‹РІР°РµС‚, РјРѕР¶РЅРѕ Р»Рё Р±РµР·РѕРїР°СЃРЅРѕ Р·Р°РїСѓСЃРєР°С‚СЊ native-runtime evaluation."""

        return self.incompatible_total == 0

    def to_payload(self) -> dict[str, Any]:
        """РџСЂРµРѕР±СЂР°Р·СѓРµС‚ preflight-РѕС‚С‡РµС‚ РІ JSON-СЃРѕРІРјРµСЃС‚РёРјСѓСЋ СЃС‚СЂСѓРєС‚СѓСЂСѓ."""

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
    """РћС€РёР±РєР° preflight, Р±Р»РѕРєРёСЂСѓСЋС‰Р°СЏ Р·Р°РїСѓСЃРє native target РїСЂРё РЅРµСЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё РїСЂРѕС„РёР»СЏ."""

    def __init__(self, *, report: NativeCompatibilityPreflightReport) -> None:
        """РРЅРёС†РёР°Р»РёР·РёСЂСѓРµС‚ РѕС€РёР±РєСѓ Рё СЃРѕС…СЂР°РЅСЏРµС‚ structured preflight report."""

        self.report = report
        super().__init__(
            "Native runtime preflight failed: РїСЂРѕС„РёР»СЊ СЃРѕРґРµСЂР¶РёС‚ participants СЃ РЅРµРїРѕРґРґРµСЂР¶Р°РЅРЅС‹РјРё node kinds."
        )


def build_native_compatibility_preflight_report(
    *,
    profile: EvaluationProfileSpec,
    profile_file_dir: Path,
) -> NativeCompatibilityPreflightReport:
    """РЎРѕР±РёСЂР°РµС‚ preflight-РѕС‚С‡РµС‚ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё profile РґР»СЏ `native_runtime` target."""

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
                                "РСЃРїСЂР°РІСЊС‚Рµ source-С„Р°Р№Р» participant-Р° РёР»Рё РІСЂРµРјРµРЅРЅРѕ РёСЃРєР»СЋС‡РёС‚Рµ РµРіРѕ РёР· native profile."
                            ),
                        )
                    ],
                    message="РќРµ СѓРґР°Р»РѕСЃСЊ СЂРµР·РѕР»РІРёС‚СЊ Graph IR participant-Р° РґР»СЏ native preflight.",
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
                    message="Participant СЃРѕРІРјРµСЃС‚РёРј СЃ native exporter v0.",
                )
            )
            continue

        issues = [
            NativeCompatibilityIssue(
                node_id=node.id,
                kind=node.kind.value,
                component_ref=node.component_ref,
                reason=f"Node kind `{node.kind.value}` РЅРµ РїРѕРґРґРµСЂР¶Р°РЅ native exporter v0.",
                recommendation=(
                    "Уберите или замените узел для native target, либо запустите participant на dsl_runtime. "
                    "Проверьте, что node kind входит в capability matrix native exporter."
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
                message="Participant РЅРµСЃРѕРІРјРµСЃС‚РёРј СЃ native exporter v0 РёР·-Р·Р° unsupported node kinds.",
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
    """Р РµР·РѕР»РІРёС‚ Graph IR participant-Р° РЅР°РїСЂСЏРјСѓСЋ РёР»Рё С‡РµСЂРµР· РєРѕРјРїРёР»СЏС†РёСЋ DSL."""

    if str(participant.graph_ir_file).strip():
        return load_graph_ir_spec(_resolve_path(base_dir, participant.graph_ir_file))

    compiler = DslToGraphIRCompiler()
    compile_result = compiler.compile_file(_resolve_path(base_dir, participant.dsl_file))
    if compile_result.graph_ir is None:
        raise ValueError(
            f"РќРµ СѓРґР°Р»РѕСЃСЊ СЃРєРѕРјРїРёР»РёСЂРѕРІР°С‚СЊ DSL СѓС‡Р°СЃС‚РЅРёРєР° `{participant.participant_id}`: {compile_result.report.summary()}"
        )
    return compile_result.graph_ir


def _participant_source(*, participant: Any, base_dir: Path) -> tuple[str, str]:
    """Р’РѕР·РІСЂР°С‰Р°РµС‚ source kind/path participant-Р° РґР»СЏ preflight РѕС‚С‡РµС‚Р°."""

    if str(participant.graph_ir_file).strip():
        return "graph_ir", str(_resolve_path(base_dir, participant.graph_ir_file))
    return "dsl", str(_resolve_path(base_dir, participant.dsl_file))


def _resolve_path(base_dir: Path, path_value: str) -> Path:
    """Р РµР·РѕР»РІРёС‚ Р°Р±СЃРѕР»СЋС‚РЅС‹Р№ РїСѓС‚СЊ РёР»Рё РїСѓС‚СЊ РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅРѕ РґРёСЂРµРєС‚РѕСЂРёРё profile."""

    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()

