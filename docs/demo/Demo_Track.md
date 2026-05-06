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
4. реальный OpenRouter-вызов в LLM узлах при наличии `OPENROUTER_API_KEY`;
5. генерация кодового артефакта агента (`DSL -> generated package -> generated runner`).
6. checkpoint/resume путь (`invoke -> checkpoint -> resume`) по `task_id`.

Пока в работе:

1. расширение trace в сторону checkpoint-aware run history.

Команды:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_runtime_demo.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_generate_agent_code.ps1
```

В runtime выводе ожидаем поля `node_events` и `trace_summary`.

### Stage D2 (I3) - Evaluation Demo

Что уже показываем:

1. валидацию golden dataset JSONL через typed loader и CLI;
2. исполняемый oracle-прогон по golden dataset (`expected_stub` для deterministic smoke/CI);
3. summary pass/fail (`cases_total/passed/failed/pass_rate`) и корректный exit code.

Команды:

```powershell
python -m optimizer.evaluation.run_oracle --dsl-file .\examples\dsl\direct_llm.yaml --dataset-file .\examples\datasets\golden_support_v1.jsonl --execution-mode expected_stub --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_oracle.ps1
```

Что уже добавлено в D2:

1. equal-budget tournament между 2-3 архитектурами (I3.S3);
2. ranking + winner с прозрачным tie-break контрактом;
3. CLI и smoke-команда для воспроизводимого сравнения.

Команды Arena:

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```

Live команды Arena:

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live.ps1
```

Что уже добавлено в D3:

1. `middle_metrics` по каждому участнику (`coverage`, `violations`, `nodes`, `latency`, `llm_calls`);
2. config-driven `scoring` policy с весами/направлениями;
3. `composite_score` и `score_breakdown` в итоговом отчете турнира.

Следующий шаг:

1. Evidence Pack v0 (I4.S2).

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

- Active stage: `D3 (I4)`
- Demo readiness: `Green`
- Next demo milestone: `D3 evidence pack` (`I4.S2`)
