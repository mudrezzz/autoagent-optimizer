# Demo Track

## Purpose

Демо-трек показывает лучшее текущее состояние проекта на каждом этапе развития.
Он развивается синхронно с roadmap, чтобы:

1. быстро демонстрировать прогресс;
2. проверять интеграцию новых слайсов на живом сценарии;
3. давать понятный вход новым разработчикам и стейкхолдерам.

## Core Demo Scenario

Базовый сценарий демо (из MVP-вертикали ТЗ):

`Complex PDF/OCR extraction -> structured database rows`

Почему выбран:

1. хорошо виден эффект от архитектурных решений;
2. естественно включает deterministic и LLM-компоненты;
3. легко показывать метрики качества/стоимости/латентности;
4. хорошо подходит для HITL и policy-gates в следующих MVP.

## Demo Evolution By Iteration

### Stage D0 (I1) - Spec Demo

Что показываем сейчас:

1. DSL v0 спецификация (`examples/dsl/*.yaml`);
2. Graph IR v0 спецификация (`examples/graph_ir/*.json`);
3. compile path DSL -> Graph IR;
4. smoke-валидация обоих уровней.

Команды:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_validate_dsl.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_validate_graph_ir.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_compile_dsl_to_ir.ps1
```

### Stage D1 (I2) - Runtime Demo

Что уже показываем:

1. компиляция DSL -> IR;
2. рендер IR -> исполняемый workflow;
3. invoke path на нескольких сценариях (`direct_llm`, `hitl_gate low/high risk`);
4. реальный OpenRouter-вызов в LLM узлах при наличии `OPENROUTER_API_KEY`.

Пока в работе:

1. resume/checkpoint сценарий;
2. node-level white-box trace слой.

### Stage D2 (I3) - Evaluation Demo

План показа:

1. прогон на golden dataset;
2. output + middle metrics;
3. equal-budget tournament между 2-3 архитектурами.

### Stage D3 (I4) - Champion Demo

План показа:

1. формирование Evidence Pack;
2. champion/challenger сравнение;
3. export champion bundle.

## Demo Contract For Every Slice

Для каждого слайса обязательно:

1. обновить, что изменилось в демо;
2. сохранить/добавить runnable команду или сценарий;
3. зафиксировать ожидаемый результат (что увидит пользователь);
4. синхронизировать ссылки в `README` и `Roadmap` при необходимости.

## Current Demo Status

- Active stage: `D1 (I2)`
- Demo readiness: `Green`
- Next demo milestone: `D2 (I3)` after completion of evaluation slices
