# ADR-0046: Stage Mapping Manual Confirmation v0

- Status: Accepted
- Date: 2026-06-04
- Slice: I5.S3a
- User Docs Page: docs/wiki/user_guides/c5s-stage-mapping.md

## Context

Stage auto-map can produce an `ambiguous` row when more than one candidate node matches the same `target_stage`.
That is expected for multi-step candidates such as `Pattern Cleaner`, where both `rewrite_draft` and `cleanup_pass` can look like synthesis nodes.

The previous behavior was wrong for HITL UX: a user could manually confirm one node and save the mapping, but validation still treated the row as `ambiguous`.
The same ambiguous row could also produce repeated validation issues when several diagnostic signals depended on the same stage.

## Decision

Manual confirmation is now a first-class Stage Mapping state transition.

When `save stage mappings` receives a row with exactly one selected node and either:

1. `source = manual`, or
2. notes contain a manual confirmation marker,

backend normalizes the row to:

1. `status = bound`,
2. `source = manual`,
3. `confidence >= 0.80`.

Auto-map still keeps ambiguous rows as `ambiguous` until the user confirms them.
Validation aggregates repeated stage mapping issues by `target_stage` and candidate instead of emitting the same error once per diagnostic signal.

## Consequences

1. Human confirmation resolves auto-map ambiguity without requiring hidden backend changes.
2. `Refresh auto-map` remains conservative and can still produce `ambiguous` rows.
3. `Save mapping` becomes the HITL boundary for confirming stage mappings.
4. Validation reports become shorter and actionable.

## Test Requirements

1. Backend unit tests must cover ambiguous auto-map, manual confirmation and validation dedupe.
2. Frontend tests must cover editing notes/node ids and saving a manually confirmed row.
3. Wiki must explain `bound`, `missing`, `ambiguous` and manual confirmation behavior.
4. Real UI screenshots must be updated when Stage Mapping UI changes.
