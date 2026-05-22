# ADR-0030: Design System as Mandatory Frontend Standard

- Status: Accepted
- Date: 2026-05-22
- Slice: V2.1.S1
- Decision Makers: AutoAgent Optimizer core team
- Supersedes: N/A

## Context

Проект перешел на вертикальную модель разработки (`BE + FE + Demo + QA`), где frontend стал обязательной частью каждого слайса.
Без единого визуального и контентного стандарта UI начинает расползаться:

1. несогласованные токены и компоненты между слайсами;
2. нестабильный UX и voice;
3. рост времени на доработки и ревью.

В репозитории уже добавлен полноценный `design_system` пакет (tokens, handoff, UI kits, assets, rules), который должен стать единым источником истины.

## Decision

Фиксируем `design_system` как обязательный стандарт для всех UI-изменений:

1. frontend реализуется только на токенах `design_system/colors_and_type.css`;
2. базовые UI-паттерны и композиции берутся из `design_system/ui_kits/*`;
3. бренд-ассеты используются из `design_system/assets/*` без ручного пересоздания;
4. copy/voice подчиняется rules из `design_system/README.md`;
5. соответствие `design_system` включается в Definition of Done и demo contract.

## Alternatives Considered

1. Оставить дизайн-систему как "рекомендованную", но не обязательную.
2. Применять дизайн-систему только для landing, но не для workbench UI.
3. Разрешить локальные визуальные отклонения без централизованного контроля.

## Consequences

### Positive

1. Единый UX/visual style на всем фронтенд-контуре.
2. Быстрее ревью и меньше регрессий в UI.
3. Четкая точка входа для новых разработчиков фронтенда.

### Negative / Trade-offs

1. Меньше свободы для ad-hoc визуальных решений.
2. Возможна дополнительная работа при миграции legacy UI к токенам.
3. Любые новые нестандартные компоненты требуют сначала расширения дизайн-системы.

## Implementation Notes

1. Обновить основные документы (`README`, `Roadmap`, `Project_Operating_Model`, `System_Architecture_Overview`, `Demo_Track`, backlog) с обязательным правилом `design_system`.
2. В каждом фронтовом слайсе фиксировать в описании используемые артефакты дизайн-системы.
3. При конфликте между текущим UI и `design_system` приоритет у `design_system`.

## Verification

1. Frontend-слайсы закрываются только при явной проверке соответствия `design_system`.
2. Demo-checklist включает визуальную и контентную проверку правил дизайн-системы.
3. Полный `python -m pytest` остается обязательным gate слайса.

## Links

1. `design_system/README.md`
2. `design_system/colors_and_type.css`
3. `design_system/ui_kits/app/README.md`
4. `design_system/ui_kits/landing/README.md`
