# ADR-0033: Mandatory Slice Wiki and GitHub Pages in Current Repository

- Status: Accepted
- Date: 2026-05-26
- Slice: V2.3.S5 (governance prerequisite)
- Decision Makers: Product + Engineering
- Supersedes: N/A
- User Docs Page: docs/wiki/governance/adr-to-wiki-policy.md

## Context

Начиная с V2-слайсов, функциональность быстро растет, и знания о пользовательском поведении теряются между ADR, Roadmap и кодом.
Нужен единый живой пользовательский контур документации, обновляемый в том же ритме, что и слайсы.

## Decision

1. Wiki публикуется из текущего репозитория через GitHub Pages.
2. Техническая платформа wiki: MkDocs (`mkdocs.yml`, `docs/wiki`, `requirements-docs.txt`).
3. Для каждого закрытого слайса обязательны wiki-обновления:
   - `docs/wiki/releases/<slice-id>.md`
   - релевантные `docs/wiki/user_guides/*`
   - релевантные `docs/wiki/developer/*`
4. ADR-шаблон расширяется обязательным полем `User Docs Page`.
5. DoD/Working Agreement обновляются: слайс не считается закрытым без wiki-обновления.

## Alternatives Considered

1. GitHub Wiki tab (`repo.wiki.git`) как отдельное хранилище.
2. Отдельный репозиторий документации.
3. Локальные markdown-документы без публикации.

## Consequences

### Positive

1. Документация и код эволюционируют синхронно.
2. Любой новый разработчик и пользователь видит актуальную логику по capability.
3. Прозрачная трассировка `Slice -> ADR -> User Docs`.

### Negative / Trade-offs

1. Увеличивается объем обязательной работы на слайс.
2. Появляется CI/CD контур для docs, который нужно поддерживать.

## Implementation Notes

1. Добавлен workflow `.github/workflows/docs-pages.yml`.
2. Добавлен начальный каркас `docs/wiki/*`.
3. Обновлены process-документы и ADR template.

## Verification

1. `mkdocs build --strict` проходит локально/в CI.
2. GitHub Pages workflow публикует сайт.
3. В завершенных слайсах есть release note в `docs/wiki/releases/*`.

## Links

1. `mkdocs.yml`
2. `.github/workflows/docs-pages.yml`
3. `docs/wiki/index.md`
4. `docs/process/Project_Operating_Model.md`
5. `docs/adr/ADR-TEMPLATE.md`
