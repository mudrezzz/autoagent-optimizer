# AutoAgent Optimizer

OSS-first платформа для архитектурного поиска, white-box оценки и итеративной оптимизации compound AI systems.

## Current Status

- `Phase`: MVP-1 (foundation)
- `Iteration`: I0 - Governance & Architecture Baseline
- `Overall`: In Progress (I0.S1 done, I0.S2 planned)
- `Next Slice`: I0.S2 Initial backlog shaping from TZ

Подробный статус:

- [Roadmap.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/Roadmap.md)
- [System_Architecture_Overview.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/System_Architecture_Overview.md)
- [ADR Index](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/README.md)
- [Project Operating Model](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/process/Project_Operating_Model.md)

## Project Rules

1. Развиваем продукт малыми слайсами, каждый слайс должен давать проверяемый инкремент.
2. Все архитектурные решения фиксируются через ADR/ARD до или вместе с реализацией.
3. `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` всегда актуальны после каждого слайса.
4. Новый разработчик должен за 10-15 минут понять текущий статус и взять следующий слайс.
5. Каждый слайс завершается отдельным git commit.
6. Развитие идет концентрическими MVP-кругами: MVP-1 -> MVP-2 -> MVP-3.

## Repository Map

- `auto_agent_optimizer_концепция_и_тз.md` - полное ТЗ и концепция.
- `Roadmap.md` - план по итерациям, слайсам, статусам.
- `System_Architecture_Overview.md` - текущая целевая архитектура.
- `docs/adr` - журнал архитектурных решений.
- `langgraph-document-ai-platform` - внешний framework-источник для изучения и переиспользования (read-only в рамках этого проекта).

## Definition of Done For a Slice

1. Реализация завершена и проверена локально.
2. Обновлены `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` (если затронуто).
3. Добавлен/обновлен ADR при архитектурных изменениях.
4. Сделан отдельный git commit с привязкой к слайсу (например `I1.S2`).
