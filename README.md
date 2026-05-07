# AutoAgent Optimizer

OSS-first платформа для архитектурного поиска, white-box оценки и итеративной оптимизации compound AI systems.

## Current Status

- `Phase`: MVP-1 (foundation)
- `Iteration`: I4 - Evidence + Export
- `Overall`: In Progress (I2.S1-I4.S2 in progress)
- `Next Slice`: I4.S2 Evidence Pack v0 + dual-metrics contract

Подробный статус:

- [Roadmap.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/Roadmap.md)
- [System_Architecture_Overview.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/System_Architecture_Overview.md)
- [ADR Index](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/README.md)
- [Project Operating Model](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/process/Project_Operating_Model.md)
- [Executable Slice Backlog](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/backlog/Executable_Slice_Backlog.md)
- [Demo Track](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/demo/Demo_Track.md)

## Project Rules

1. Развиваем продукт малыми слайсами, каждый слайс должен давать проверяемый инкремент.
2. Все архитектурные решения фиксируются через ADR/ARD до или вместе с реализацией.
3. `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` всегда актуальны после каждого слайса.
4. Новый разработчик должен за 10-15 минут понять текущий статус и взять следующий слайс.
5. Каждый слайс завершается отдельным git commit.
6. Развитие идет концентрическими MVP-кругами: MVP-1 -> MVP-2 -> MVP-3.
7. Демо развивается синхронно с функционалом и обновляется на каждом слайсе.

## Repository Map

- `auto_agent_optimizer_концепция_и_тз.md` - полное ТЗ и концепция.
- `Roadmap.md` - план по итерациям, слайсам, статусам.
- `System_Architecture_Overview.md` - текущая целевая архитектура.
- `docs/adr` - журнал архитектурных решений.
- `langgraph-document-ai-platform` - внешний framework-источник для изучения и переиспользования (read-only в рамках этого проекта).
- `optimizer/dsl` - DSL v0 schema, loader и CLI-валидация.
- `optimizer/graph_ir` - runtime-neutral Graph IR v0, валидаторы и CLI.
- `optimizer/dsl/compiler.py` - компилятор DSL -> Graph IR и отчет компиляции.
- `optimizer/renderer/langgraph_dai` - runtime renderer и запуск Graph IR workflow.
- `optimizer/codegen` - DSL/IR -> сгенерированный код агента (package + runner).
- `optimizer/tracing` - node-level события исполнения и сводка trace по run.
- `optimizer/evaluation` - golden dataset contract, loader, oracle runner и CLI-валидация/прогон.
- `optimizer/metrics` - middle-метрики и служебные агрегаторы для arena scoring.
- `components` - deterministic demo-компоненты для пайплайнов (включая AI-pattern инструменты).
- `validators` - python-валидаторы demo-сценариев (включая style output guard).
- `docs/specs/Evaluation_Profile_v0.md` - концепт profile-driven оценки (task-specific metrics + pluggable evaluators).
- `examples/dsl` - эталонные YAML-спеки, включая stylizer кандидатов (`style_direct_llm`, `style_pattern_cleaner`, `style_hitl_reviewer`).
- `examples/graph_ir` - эталонные Graph IR JSON-спеки.
- `examples/datasets` - эталонные golden dataset JSONL кейсы (включая `golden_linkedin_stylizer_v1.jsonl`).
- `examples/resources/ai_style_patterns_ru_v1.json` - справочник известных AI-паттернов для stylizer-кейса.
- `scripts/smoke_validate_dsl.ps1` - smoke-проверка всех DSL-примеров.
- `scripts/smoke_validate_graph_ir.ps1` - smoke-проверка всех Graph IR-примеров.
- `scripts/smoke_compile_dsl_to_ir.ps1` - smoke-компиляция DSL в IR.
- `scripts/smoke_run_runtime_demo.ps1` - smoke runtime-демо исполнения workflow.
- `scripts/smoke_generate_agent_code.ps1` - smoke-демо генерации и запуска кодового агента.
- `scripts/smoke_validate_dataset.ps1` - smoke-валидация golden dataset.
- `scripts/smoke_run_oracle.ps1` - smoke-прогон executable oracle runner.


## I3.S3 Artifacts

- `optimizer/arena` - equal-budget tournament runner и CLI сравнения 2-3 архитектур.
- `examples/arena/support_tournament_v0.yaml` - live-конфигурация турнира stylizer-кейса.
- `examples/arena/support_tournament_ci_v0.yaml` - стабильная CI-конфигурация stylizer-турнира.
- `scripts/smoke_run_arena.ps1` - smoke-прогон CI stylizer турнира.
- `docs/specs/Architecture_Arena_v0.md` - config-first контракт `budget`/`ranking`/`evaluator` политик турнира.

## I4.S1 Artifacts

- `optimizer/metrics/middle_metrics.py` - расчет middle-метрик (`coverage`, `violations`, `nodes`, `latency`, `llm_calls`).
- `optimizer/arena/tournament_schema.py` - расширенный контракт `scoring` policy и ranking по `composite_score`.
- `optimizer/arena/runner.py` - расчет `middle_metrics`, `composite_score` и `score_breakdown` в tournament output.
- `examples/arena/support_tournament_v0.yaml` - демо-конфиг с включенным `scoring`.

## Dual Metrics Model

В проекте закреплена модель двух типов метрик:

1. `Comparative Metrics` - только для сравнения архитектур и ranking.
2. `Diagnostic Signals` - только для локализации bottleneck и планирования intervention.

Фиксация решения: `ADR-0016`.

## Configurable Evaluation Model

Оценка в платформе развивается как `profile-driven` слой:

1. Метрики comparative/diagnostic задаются под конкретный task type.
2. Методы оценки подключаются как adapters (`golden_oracle`, `llm_judge`, `executable`, `render`, ...).
3. Изменение профиля метрик рассматривается как agent workflow с обязательным HITL approve.

Текущая спецификация направления:

- [Evaluation_Profile_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Evaluation_Profile_v0.md)

## Definition of Done For a Slice

1. Реализация завершена и проверена локально.
2. Обновлены `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` (если затронуто).
3. Добавлен/обновлен ADR при архитектурных изменениях.
4. Сделан отдельный git commit с привязкой к слайсу (например `I1.S2`).
5. Выполнен полный прогон автотестов (`unit + integration + e2e`).

## Test Policy

Структура тестов:

1. `tests/unit`
2. `tests/integration`
3. `tests/e2e`

Полный прогон (обязательно после каждого слайса):

```powershell
python -m pytest
```

Прогон по уровням:

```powershell
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m e2e
```

Live runtime-тесты (опционально, неблокирующие):

```powershell
$env:RUN_LIVE_ARENA="1"
python -m pytest -m live
```

## PowerShell JSON Tip

Для CLI-команд, где передается JSON payload, в PowerShell используйте `--payload-file` как основной способ запуска.
Это исключает ошибки экранирования вида `unrecognized arguments`.

## Runtime Demo Quickstart (PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path .\tmp | Out-Null
'{"draft_post":"В современном мире нельзя недооценивать роль редактуры. Давайте разберемся, как переписать пост живее и сохранить факты."}' | Set-Content -LiteralPath .\tmp\runtime_payload.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\style_direct_llm.yaml --payload-file .\tmp\runtime_payload.json --pretty
```

Полный smoke-прогон демо:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_runtime_demo.ps1
```

## Oracle Demo Quickstart (PowerShell)

Быстрая проверка исполняемой оценки на golden dataset (детерминированный режим для smoke/CI):

```powershell
python -m optimizer.evaluation.run_oracle --dsl-file .\examples\dsl\style_direct_llm.yaml --dataset-file .\examples\datasets\golden_linkedin_stylizer_v1.jsonl --execution-mode expected_stub --pretty
```

Полный smoke-прогон oracle:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_oracle.ps1
```


## Arena Demo Quickstart (PowerShell)

Стабильный CI-турнир (deterministic `expected_stub`):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_v0.yaml --pretty
```

В успешном выводе проверьте:

1. `scoring_enabled: true`
2. `ranking_policy[0].name: composite_score`
3. у каждого участника есть `middle_metrics`, `composite_score`, `score_breakdown`
4. есть секции `comparison` и `diagnostics`
5. в `diagnostics.participants[].signals` есть `top_bottlenecks` и `intervention_hints`

Live runtime-демо (winner может меняться из-за LLM):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_v0.yaml --pretty
```

Полный smoke-прогон arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```

Live smoke-прогон arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live.ps1
```

Resume quickstart:

```powershell
'{"query":"Create safe ticket","action_risk":"low"}' | Set-Content -LiteralPath .\tmp\start.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\hitl_gate.yaml --payload-file .\tmp\start.json --task-id demo-resume-task --checkpoint-dir .\tmp\runtime_checkpoints --pretty

'{"action_risk":"high","review_decision":"approve"}' | Set-Content -LiteralPath .\tmp\resume.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\hitl_gate.yaml --resume-task-id demo-resume-task --payload-file .\tmp\resume.json --checkpoint-dir .\tmp\runtime_checkpoints --pretty
```

## OpenRouter Setup (For Real LLM Calls)

Когда перейдем к runtime-слайсам (`I2.*`), можно включить реальные вызовы LLM.

1. Скопируйте `.env.example` в `.env`.
2. Заполните `OPENROUTER_API_KEY`.
3. При необходимости смените `OPENROUTER_MODEL`.

Важно: `.env` добавлен в `.gitignore` и не должен попадать в git.
