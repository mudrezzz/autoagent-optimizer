# ADR / ARD Index

Этот каталог хранит архитектурные решения проекта.

Терминология:

- `ADR` (Architecture Decision Record) - базовый формат.
- `ARD` - допустимое внутреннее синонимичное название в проекте.

## Rules

1. Любое существенное архитектурное решение фиксируется отдельным ADR.
2. ADR создается до реализации или в том же слайсе, где решение внедрено.
3. ADR не переписывается задним числом; изменения оформляются новым ADR (supersedes).
4. Каждый ADR связан со слайсом roadmap (`I*.S*`) и commit hash.

## Status Values

- `Proposed`
- `Accepted`
- `Superseded`
- `Deprecated`

## File Naming

`ADR-XXXX-short-title.md`, где `XXXX` - четырехзначный номер.

## ADR List

1. [ADR-0001-use-langgraph-dai-as-render-target.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0001-use-langgraph-dai-as-render-target.md) - Accepted
2. [ADR-0002-dsl-v0-yaml-first.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0002-dsl-v0-yaml-first.md) - Accepted
3. [ADR-0003-mandatory-test-pyramid-and-full-gate.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0003-mandatory-test-pyramid-and-full-gate.md) - Accepted

## Template

Использовать:

- [ADR-TEMPLATE.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-TEMPLATE.md)
