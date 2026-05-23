# ADR-0032: Risk-Based Test Gates for Slice Delivery

- Status: Accepted
- Date: 2026-05-23
- Slice: V2.3.S1a follow-up governance update
- Decision Makers: AutoAgent Optimizer core team
- Supersedes: ADR-0003 (partially, in the "full test run after every slice" clause)

## Context

We run many small vertical slices, including frequent frontend-only iterations.
The previous policy required a full `python -m pytest` run after every slice.
That keeps quality high, but for tiny UI edits it creates unnecessary cycle time
and slows down delivery feedback.

At the same time, we must preserve strict QA discipline and avoid ad-hoc checks.

## Decision

Adopt a risk-based test gate model for commits:

1. `Fast gate` for frontend-only micro changes without API contract changes.
2. `Targeted gate` for frontend + API slice changes (or local backend changes).
3. `Full gate` for major slices, release candidates, and deep runtime/evaluation/export changes.

Gate details are documented in:

1. `README.md` (`Test Policy`).
2. `Roadmap.md` (`Working Agreement Per Iteration`).
3. `docs/process/Project_Operating_Model.md` (`Test Pyramid Policy`).
4. `docs/specs/Frontend_Architecture_v0.md` (`Testing Strategy`).

## Alternatives Considered

1. Keep full `python -m pytest` mandatory for every slice.
2. Let each developer choose arbitrary local checks without policy.

## Consequences

### Positive

1. Faster feedback loop for frontend slices.
2. Explicit, non-ad-hoc mapping from change scope to QA gate.
3. Better alignment with vertical delivery pace.

### Negative / Trade-offs

1. Requires discipline in classifying the slice risk correctly.
2. Wrong gate selection can miss regressions unless reviewers enforce policy.

## Implementation Notes

1. Documentation updated to remove policy contradictions.
2. Frontend/API restart caveat added (to avoid false `404` from stale dev server process).
3. Existing full regression path remains mandatory for high-risk slices.

## Verification

1. Documentation consistency check across `README`, `Roadmap`, and process docs.
2. Frontend failure case (stale backend process causing `404`) is now explicitly documented in the testing flow.

## Links

1. `README.md`
2. `Roadmap.md`
3. `docs/process/Project_Operating_Model.md`
4. `docs/specs/Frontend_Architecture_v0.md`
5. `docs/adr/ADR-0003-mandatory-test-pyramid-and-full-gate.md`
