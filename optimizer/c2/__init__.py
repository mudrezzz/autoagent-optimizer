"""Публичные экспорты C2 (chat brief -> candidate draft + compile gate)."""

from optimizer.c2.candidate_assembly import run_compile_readiness_gate_for_candidate_set
from optimizer.c2.candidate_draft import build_candidate_draft_from_brief

__all__ = ["build_candidate_draft_from_brief", "run_compile_readiness_gate_for_candidate_set"]
