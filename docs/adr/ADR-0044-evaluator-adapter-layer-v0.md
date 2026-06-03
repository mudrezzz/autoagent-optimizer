# ADR-0044: Evaluator Adapter Layer v0

- Status: Accepted
- Date: 2026-06-03
- Slice: I5.S2
- User Docs Page: docs/wiki/user_guides/c6-evaluators-matrix.md

## Context

C6 previously stored evaluators as simple checkbox rows and matrix cells as arbitrary links.
That was not enough for task-specific evaluation because different evaluator methods have different requirements and cannot score every metric.

Examples:

1. `golden_oracle` needs assigned datasets and can compare expected payloads, but it is not a runtime telemetry source for cost/latency.
2. `llm_judge` needs LLM credentials and budget.
3. `executable_validator` can validate runtime/test/render-like signals, but it is not a semantic judge by default.

Without an explicit adapter contract, UI could show a matrix that looked valid while backend could not execute it correctly.

## Decision

Introduce `Evaluator Adapter Layer v0` as the source of truth for C6 evaluator semantics.

Each evaluator is enriched with:

1. `adapter_kind`,
2. `requires_dataset`,
3. `requires_llm`,
4. `requires_stage_mapping`,
5. `supported_metric_refs`,
6. `budget_cost_model`,
7. `adapter_status`,
8. `adapter_status_reason`.

Each `evaluator_metric_link` is enriched with:

1. `compatibility_status`,
2. `compatibility_reason`.

Backend normalization must sanitize incompatible evaluator x metric links to `enabled=false`.
Validation still reports evaluator requirement gaps and uncovered enabled metrics.

The frontend must render adapter metadata and prevent users from enabling unsupported matrix cells.

## Consequences

1. C6 becomes a real evaluator orchestration screen, not a generic checkbox table.
2. Optimizer preflight now uses dataset-aware evaluation validation.
3. Old stored profiles are normalized through the adapter catalog during state loading.
4. `GET /api/evaluation/evaluator-adapters` exposes the adapter catalog for future UI/API expansion.
5. Future evaluator execution code must bind to this adapter catalog instead of inventing ad-hoc evaluator semantics.
6. Autofill actions must only enable compatible links and must leave unsupported links unchecked.

## Test Requirements

1. Unit tests must verify adapter enrichment and incompatible-link sanitization.
2. Integration tests must verify API payloads include adapter metadata and compatibility fields.
3. Frontend tests must verify adapter metadata is visible and unsupported matrix cells are disabled.
4. UI screenshot docs must be updated when C6 rendering changes.

## Amendment: I5.S2b Safe Autofill

Unsupported matrix cells are not a user-level validation problem.
They are an impossible state.

Therefore:

1. unsupported links are always persisted as `enabled=false`,
2. `autofill_matrix_links` enables only compatible links,
3. UI renders unsupported cells as unchecked and disabled,
4. `Validate profile` focuses on real coverage gaps instead of obvious unsupported checkboxes.
