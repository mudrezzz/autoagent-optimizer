# Demo Track

## Purpose

Демо-трек показывает лучшее текущее состояние проекта на каждом этапе развития.
Он развивается синхронно с roadmap, чтобы:

1. быстро демонстрировать прогресс;
2. проверять интеграцию новых слайсов на живом сценарии;
3. давать понятный вход новым разработчикам и стейкхолдерам.

## Core Demo Scenario

Базовый сценарий демо (из MVP-вертикали ТЗ):

`AI style rewrite for LinkedIn/Telegram posts`

Почему выбран:

1. можно быстро увидеть логические провалы на понятном человеку результате;
2. метрики явно task-specific (смысл, энергия, факты, длина, AI-паттерны);
3. естественно показывает разницу comparative vs diagnostic слоев;
4. хорошо подходит для будущего MetricOps + HITL цикла.

## Secondary Demo Scenario

Дополнительный сценарий:

`Complex PDF/OCR extraction -> structured database rows`

Его сохраняем как расширенный enterprise-кейс для следующих MVP.

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
python -m optimizer.evaluation.run_oracle --dsl-file .\examples\dsl\style_direct_llm.yaml --dataset-file .\examples\datasets\golden_linkedin_stylizer_v1.jsonl --execution-mode expected_stub --pretty
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

Decision-profile команды Arena (для более надежного архитектурного решения):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --pretty
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_decision_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_decision.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_decision.ps1
```

Full-budget команды Arena (дороже, для контрольных прогонов):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_full_v0.yaml --pretty
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_full_v0.yaml --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_full.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_full.ps1
```

Что уже добавлено в D3:

1. `middle_metrics` по каждому участнику (`coverage`, `violations`, `nodes`, `latency`, `llm_calls`);
2. config-driven `scoring` policy с весами/направлениями;
3. `composite_score` и `score_breakdown` в итоговом отчете турнира.
4. расширенный stylizer dataset (12 длинных кейсов) + раздельные smoke/full budget профили.
5. Evidence Pack v0 (`evidence_pack.json` + `evidence_pack.md`) с разделением `comparison` и `diagnostics`.
6. explainable winner/challenger diff и приоритетные рекомендации для challenger.
7. разделение run-policy:
   - `smoke-live`: cheap model + 4 кейса,
   - `decision-live`: quality model + 8 кейсов (`hash_stable`).

Следующий шаг:

1. Native component bindings expansion (I4.S6).

### Stage D3 (I4) - Champion Demo

Что уже показываем:

1. формирование Evidence Pack;
2. champion/challenger сравнение;
3. export champion bundle с `diagnostic_map.json`, `winner_graph_ir.json` и `generated_agent/*`;
4. reproducible handoff через `bundle_manifest.json`.

Команды:

```powershell
python -m optimizer.champion.export_bundle --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --out-dir .\tmp\champion_bundle --bundle-name stylizer_ci_bundle --force --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_export_champion_bundle.ps1
```

### Stage D4 (I5) - Evaluation Fabric Demo

План показа:

1. profile-driven оценка для двух разных задач:
   - OCR/support,
   - style rewrite social post.
2. переключение evaluator methods без правки кода (`golden_oracle`, `llm_judge`, `executable`, `render`).
3. metric-crafting agent draft + HITL approve для активации profile.
4. post-export native re-benchmark: прогон native champion на тех же evaluation profiles, сравнение с DSL baseline и gate-решение (`promote` / `rework`).

Что уже показываем:

1. typed `Evaluation Profile v0` для stylizer/ocr кейсов;
2. запуск одного profile на двух target:
   - `dsl_runtime`,
   - `native_runtime`;
3. unified profile-run envelope с `comparison` + `diagnostics`.
4. native preflight v0: до запуска `native_runtime` строится compatibility report по participants.
5. canonical stylizer profile (`stylizer_profile_ci_v0`) в native режиме теперь завершается контролируемым preflight-block, а не runtime-crash.

Команды:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target dsl_runtime --pretty
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target native_runtime --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile_native_preflight.ps1
```

Ожидаемо до реализации `I4.S6a`:

1. `dsl_runtime` команда должна проходить стабильно.
2. `native_runtime` команда на несовместимом профиле должна завершаться `native_compatibility_preflight_failed`.
3. следующий шаг — `I4.S6a` (устранение несовместимости по существу, чтобы canonical profile проходил на native без workaround policy).

### Stage D3.5 (I4.S4-I4.S8) - Native Export Independence Demo

План показа:

1. export native standalone агента на `langgraph-dai` без импортов `optimizer.*`;
2. запуск standalone runtime из bundle в отдельном окружении;
3. parity report `dsl_vs_native` по структурным сигналам исполнения;
4. переключение champion bundle default на native target.

Что уже показываем:

1. champion bundle содержит `native_agent/` standalone runtime пакет;
2. smoke сценарий запускает standalone native runner из bundle;
3. `parity_report.json` включает `native_runtime_smoke`.

## Demo Contract For Every Slice

Для каждого слайса обязательно:

1. обновить, что изменилось в демо;
2. сохранить/добавить runnable команду или сценарий;
3. зафиксировать ожидаемый результат (что увидит пользователь);
4. синхронизировать ссылки в `README` и `Roadmap` при необходимости.

## Current Demo Status

- Active stage: `D4 bootstrap (I5 evaluation profile v0)`
- Demo readiness: `Yellow` (native parity track pending)
- Next demo milestone: `D3.5 canonical stylizer parity` (`I4.S6a`)
