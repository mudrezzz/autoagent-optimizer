"""Публичные экспорты C2 (chat brief -> candidate draft + internal test-selection prep)."""

from optimizer.c2.candidate_assembly import select_candidates_for_tests_and_prepare
from optimizer.c2.candidate_draft import build_candidate_draft_from_brief

__all__ = ["build_candidate_draft_from_brief", "select_candidates_for_tests_and_prepare"]
