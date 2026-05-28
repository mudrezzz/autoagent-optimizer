# ADR-0042: Dataset v2 Stage-aware Target Schema

- Status: Accepted
- Date: 2026-05-28
- Slice: V2.4.S5
- Decision Makers: Product + Engineering
- Supersedes: ADR-0035 (extends dataset contract)
- User Docs Page: docs/wiki/user_guides/c4-dataset-studio.md

## Context

Dataset rows in C4 were limited to `input + expected` text.  
This is insufficient for evaluator/metric combinations that operate on intermediate stages:

1. Retrieval diagnostics require expected evidence references.
2. Rerank diagnostics require expected ranking targets.
3. Synthesis diagnostics require constraint-level expectations.
4. Final answer metrics still require classic expected answer text.

## Decision

Adopt dataset v2 row schema with stage-aware expected payload:

1. Add `target_stage` per row: `retrieval | rerank | synthesis | final`.
2. Add `expected_payload` object with stage-specific keys.
3. Keep `expected` as editor-friendly mirror for backward compatibility and quick manual input.
4. Validate dataset rows with stage-specific rules and warnings/errors.

## Consequences

### Positive

1. C4 datasets become compatible with broader evaluator matrix scenarios.
2. Diagnostics can be tied to explicit ground truth for intermediate stages.
3. Legacy rows are still accepted and migrated into `target_stage=final`.

### Negative / Trade-offs

1. Dataset editor UX gets more complex (stage selector + payload semantics).
2. Additional validation rules and tests are required.

## Verification

1. `tests/unit/test_workspace_registry_store.py` covers stage-aware persistence and validation.
2. `tests/integration/test_frontend_dev_server.py` covers stage-aware API payloads.
3. `frontend/src/__tests__/app.workspace.test.tsx` ensures C4 workspace flow remains stable.
