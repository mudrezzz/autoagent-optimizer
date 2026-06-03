# ADR-0045: Metric-Crafting HITL Loop v0

- Status: Accepted
- Date: 2026-06-03
- Slice: I5.S3
- User Docs Page: docs/wiki/user_guides/c5-metrics.md

## Context

Metrics are task-specific. A fixed global metric list is not enough for battles such as the LinkedIn/Telegram post stylizer, where useful signals include human-likeness, narrative preservation, AI-pattern reduction and over-sanitization risk.

At the same time, metrics affect ranking, budgets and evaluator coverage. The system must not silently mutate the active evaluation profile just because an assistant suggested new metrics.

## Decision

Introduce `Metric-Crafting Agent + HITL loop v0`.

The loop has two explicit phases:

1. `Suggest metrics` creates a draft metric proposal.
2. `Apply selected` mutates the active evaluation profile only for user-selected proposal items.

A metric proposal is stored with:

1. `proposal_id`, `status`, `source`, `created_at`, `summary`.
2. proposal items containing `metric_kind`, `metric_id`, `title`, `description`, `weight`, `target_stage`, `recommended_evaluators`, `required_features`, `rationale`.

The C5 contextual chat action may create the same draft proposal, but it must not apply it automatically.

Backend apply must:

1. add comparative metrics and diagnostic signals to the active profile,
2. preserve candidate-feature availability checks,
3. refresh evaluator x metric compatibility links,
4. create an evaluation profile version with source `metric_crafting_apply`,
5. mark the proposal as `applied`.

## Consequences

1. Metric creation becomes an auditable HITL workflow instead of hidden profile mutation.
2. User can reject individual proposal items before profile changes.
3. Evaluator coverage changes are visible immediately after applying proposal items.
4. Future LLM-based metric generation can replace the deterministic v0 crafter behind the same proposal/apply contract.
5. Metrics Studio remains the owner of metric profile changes; Evaluators Studio remains the owner of evaluator coverage.

## Test Requirements

1. Unit tests must verify proposal creation does not mutate the profile before apply.
2. Unit tests must verify selected proposal items are applied and versioned.
3. Integration tests must verify `/evaluation/metrics/suggest` and `/evaluation/metrics/proposals/{proposal_id}/apply`.
4. Frontend tests must verify the C5 Metrics proposal UI renders, selection works, and apply calls the backend.
5. Wiki screenshots must be updated with a real Metrics screen showing the proposal block.
