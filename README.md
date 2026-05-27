# AutoAgent Optimizer

OSS-first платформа для архитектурного поиска, white-box оценки и итеративной оптимизации compound AI systems.

## Current Status

- `Phase`: MVP-2 transition (product realignment + evaluation fabric)
- `Iteration`: Roadmap v3 - vertical product slices
- `Overall`: In Progress (V2.3.S1 + V2.3.S1a + V2.3.S2 + V2.3.S2b + V2.3.S2c + V2.3.S2d + V2.3.S3 + V2.3.S4 + V2.3.S4a + V2.3.S5 + V2.3.S5a + V2.3.S6 + V2.3.S6a + V2.3.S7 done, wizard IA decoupling planned in V2.4)
- `Next Slice`: V2.4.S1 Wizard Engine v0 (menu as stateful flow)

Подробный статус:

- [Roadmap.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/Roadmap.md)
- [System_Architecture_Overview.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/System_Architecture_Overview.md)
- [Frontend_Architecture_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Frontend_Architecture_v0.md)
- [ADR Index](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/README.md)
- [Project Operating Model](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/process/Project_Operating_Model.md)
- [Executable Slice Backlog](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/backlog/Executable_Slice_Backlog.md)
- [Demo Track](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/demo/Demo_Track.md)
- [Wiki Source](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/wiki/index.md)

## Project Rules

1. Развиваем продукт малыми слайсами, каждый слайс должен давать проверяемый инкремент.
2. Все архитектурные решения фиксируются через ADR/ARD до или вместе с реализацией.
3. `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` всегда актуальны после каждого слайса.
4. Новый разработчик должен за 10-15 минут понять текущий статус и взять следующий слайс.
5. Каждый слайс завершается отдельным git commit.
6. Развитие идет концентрическими MVP-кругами: MVP-1 -> MVP-2 -> MVP-3.
7. Демо развивается синхронно с функционалом и обновляется на каждом слайсе.
8.   backend-     frontend    .
9.  frontend   `design_system` (tokens, , , voice)    .
10. UX- frontend   North Star  [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png)    [Frontend_Architecture_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Frontend_Architecture_v0.md).
11. Для каждого слайса обязательно обновляем wiki (`docs/wiki`) и фиксируем страницу в ADR через поле `User Docs Page`.
12. Для UI-слайса обязательно обновляем реальные скриншоты в `docs/wiki/assets/screenshots/*` (не макеты), и ссылки на них в user guides.

## GitHub Wiki (Pages)

Wiki публикуется из текущего репозитория через GitHub Pages (MkDocs).

Локальный запуск:

```bash
python -m pip install -r requirements-docs.txt
mkdocs serve
```

Build-проверка:

```bash
mkdocs build --strict
```

Публикация в GitHub:

1. В репозитории откройте `Settings -> Pages`.
2. Убедитесь, что source управляется через `GitHub Actions`.
3. После push в `master` workflow `docs-pages` публикует сайт.

## Design System Compliance

`design_system`      /  .

 :

1.     [colors_and_type.css](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/colors_and_type.css),    //.
2.   - `Geist`  `Geist Mono`  scale  -.
3.  UI-  `design_system/ui_kits/app`  `design_system/ui_kits/landing`   .
4.  content rules: sentence case,  emoji,   hype-.
5.   : bluish-purple gradients, glassmorphism, heavy shadow styles,  status-pills.
6.    Lucide stroke-only (`currentColor`)   -.
7.   PR/     `design_system`   .
8.  layout  user flow   North Star  [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png) ( workspace-nav,  run-workbench,  intervention rail).

## Capability Board (Roadmap v3)

    capability   : `BE / FE / Demo / QA`.

1. `C1` Battle Registry
2. `C2` Task Chat + Candidate Generation
3. `C3` Pattern Library + RAG Retrieval
4. `C4` Dataset Studio
5. `C5` Metrics Studio
6. `C6` Evaluators Studio
7. `C7` Optimizer Run Monitor
8. `C8` Report + Champion Export/Import

## Repository Map

- `auto_agent_optimizer_концепция_и_тз.md` - полное ТЗ и концепция.
- `Roadmap.md` - план по итерациям, слайсам, статусам.
- `System_Architecture_Overview.md` - текущая целевая архитектура.
- `docs/adr` - журнал архитектурных решений.
- `design_system` -  - (, , UI kits, handoff); frontend    .
- `docs/specs/Frontend_Architecture_v0.md` -  - (`React/TypeScript`, capability unlock, UX North Star).
- `langgraph-document-ai-platform` - внешний framework-источник для изучения и переиспользования (read-only в рамках этого проекта).
- `optimizer/dsl` - DSL v0 schema, loader и CLI-валидация.
- `optimizer/graph_ir` - runtime-neutral Graph IR v0, валидаторы и CLI.
- `optimizer/dsl/compiler.py` - компилятор DSL -> Graph IR и отчет компиляции.
- `optimizer/renderer/langgraph_dai` - runtime renderer и запуск Graph IR workflow.
- `optimizer/codegen` - DSL/IR -> сгенерированный код агента (package + runner).
- `optimizer/tracing` - node-level события исполнения и сводка trace по run.
- `optimizer/evaluation` - golden dataset contract, loader, oracle runner и CLI-валидация/прогон.
- `optimizer/evaluation/profile_schema.py` - typed contract `Evaluation Profile v0`.
- `optimizer/evaluation/profile_runner.py` - profile orchestration   `dsl_runtime`/`native_runtime`.
- `optimizer/evaluation/native_compatibility.py` - preflight compatibility report  `native_runtime` target.
- `optimizer/evaluation/run_profile.py` - CLI profile-driven .
- `optimizer/metrics` - middle-метрики и служебные агрегаторы для arena scoring.
- `optimizer/evidence` - генерация Evidence Pack (`comparison` + `diagnostics` + explainable diff).
- `optimizer/champion` - export Champion Bundle (`diagnostic_map`, `winner_graph_ir`, `generated_agent`, `manifest`).
- `frontend` - app-v3-aligned React/TypeScript workbench, evolving toward product capabilities C1..C8 (legacy labels for C4/C5/C6 are still supported during migration).
- `optimizer/frontend/dev_server.py` - lightweight frontend dev server (serves `frontend/dist` build + capability API endpoints).
- `optimizer/workspace` - JSON-backed battle/arena registry store for C1 product capability.
- `optimizer/c2` - deterministic C2 brief-to-candidates generator, compile-readiness gate and arena-chat draft utilities.
- `components` - deterministic demo-компоненты для пайплайнов (включая AI-pattern инструменты).
- `validators` - python-валидаторы demo-сценариев (включая style output guard).
- `docs/specs/Evaluation_Profile_v0.md` - концепт profile-driven оценки (task-specific metrics + pluggable evaluators).
- `examples/profiles` - example evaluation profiles (`stylizer_profile_ci_v0`, `ocr_support_profile_ci_v0`).
- `scripts/smoke_run_evaluation_profile.ps1` - smoke- profile-driven path.
- `scripts/smoke_run_evaluation_profile_native_preflight.ps1` - smoke- preflight-  native profile.
- `docs/specs/Evidence_Pack_v0.md` - контракт артефактов evidence для winner/challenger анализа.
- `docs/specs/Champion_Export_Bundle_v0.md` - контракт champion bundle v0.
- `docs/specs/Native_Langgraph_DAI_Export_v0.md` - standalone native export contract без runtime-  optimizer.
- `docs/specs/Post_Export_Evaluation_Loop_v0.md` -    native champion  .
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
- `scripts/smoke_export_champion_bundle.ps1` - smoke-прогон champion bundle export.
- `scripts/smoke_frontend_shell.ps1` - smoke-прогон capability frontend shell (`C1..C8` target model, backward compatible with legacy labels).


## I3.S3 Artifacts

- `optimizer/arena` - equal-budget tournament runner и CLI сравнения 2-3 архитектур.
- `examples/arena/support_tournament_v0.yaml` - live-конфигурация турнира stylizer-кейса.
- `examples/arena/support_tournament_ci_v0.yaml` - стабильная CI-конфигурация stylizer-турнира.
- `examples/arena/support_tournament_decision_v0.yaml` - live decision-профиль (8 , `hash_stable`) для архитектурных решений.
- `examples/arena/support_tournament_ci_decision_v0.yaml` - CI decision-профиль (8 , `hash_stable`).
- `examples/arena/support_tournament_full_v0.yaml` - live full-budget конфигурация stylizer-турнира.
- `examples/arena/support_tournament_ci_full_v0.yaml` - CI full-budget конфигурация stylizer-турнира.
- `scripts/smoke_run_arena.ps1` - smoke-прогон CI stylizer турнира.
- `scripts/smoke_run_arena_decision.ps1` - smoke-прогон CI decision-профиля stylizer-турнира.
- `scripts/smoke_run_arena_live_decision.ps1` - smoke-прогон live decision-профиля stylizer-турнира.
- `scripts/smoke_generate_evidence_pack.ps1` - smoke-генерация Evidence Pack по CI arena конфигу.
- `docs/specs/Architecture_Arena_v0.md` - config-first контракт `budget`/`ranking`/`evaluator` политик турнира.

## I4.S1 Artifacts

- `optimizer/metrics/middle_metrics.py` - расчет middle-метрик (`coverage`, `violations`, `nodes`, `latency`, `llm_calls`).
- `optimizer/arena/tournament_schema.py` - расширенный контракт `scoring` policy и ranking по `composite_score`.
- `optimizer/arena/runner.py` - расчет `middle_metrics`, `composite_score` и `score_breakdown` в tournament output.
- `examples/arena/support_tournament_v0.yaml` - демо-конфиг с включенным `scoring`.
- `examples/arena/support_tournament_full_v0.yaml` - full-budget демо-конфиг с включенным `scoring`.

## I4.S2 Artifacts

- `optimizer/evidence/pack_builder.py` - сборка Evidence Pack payload и explainable winner/challenger diff.
- `optimizer/evidence/generate_pack.py` - CLI генерации `evidence_pack.json` + `evidence_pack.md`.
- `docs/specs/Evidence_Pack_v0.md` - контракт структуры evidence pack для MVP v0.
- `scripts/smoke_generate_evidence_pack.ps1` - smoke-прогон генерации evidence pack.

## I4.S3 Artifacts

- `optimizer/champion/diagnostic_map.py` - builder приоритизированной diagnostic map для winner.
- `optimizer/champion/export_bundle.py` - CLI экспорта champion bundle из arena результата.
- `docs/specs/Champion_Export_Bundle_v0.md` - контракт bundle артефактов и структура каталога.
- `scripts/smoke_export_champion_bundle.ps1` - smoke-проверка champion bundle export.

## I4.S4 Direction (Done)

- native export target `langgraph_dai_native` (standalone runtime artifact).
- parity contract `DSL path vs native exported path`.
- champion bundle default switch to native runtime artifact.

## I4.S5 Artifacts

- `optimizer/champion/native_export.py` - minimal standalone native exporter  `framework`/`infra.openrouter`.
- `optimizer/champion/export_bundle.py` - bundle   `native_agent`  `native_runtime_smoke` .
- `tests/unit/test_native_export.py` - unit- native exporter.

## Dual Metrics Model

В проекте закреплена модель двух типов метрик:

1. `Comparative Metrics` - только для сравнения архитектур и ranking.
2. `Diagnostic Signals` - только для локализации bottleneck и планирования intervention.

Фиксация решения: `ADR-0016`.

## Configurable Evaluation Model

Оценка в платформе развивается как `profile-driven` слой:

1. Метрики comparative/diagnostic задаются под конкретный task type.
2. Методы оценки подключаются как adapters (`golden_oracle`, `llm_judge`, `executable`, `render`, ...).
3. зменение профиля метрик рассматривается как agent workflow с обязательным HITL approve.

Текущая спецификация направления:

- [Evaluation_Profile_v0.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/specs/Evaluation_Profile_v0.md)

## Definition of Done For a Slice

1. Реализация завершена и проверена локально.
2.  backend-     frontend    .
3.  demo-      .
4.      `design_system` (tokens + typography + components + voice).
5. Обновлены `Roadmap.md`, `README.md`, `System_Architecture_Overview.md` (если затронуто).
6. Добавлен/обновлен ADR при архитектурных изменениях.
7. Сделан отдельный git commit с привязкой к слайсу (например `I1.S2`).
8. Выполнен тест-гейт согласно типу слайса (fast/targeted/full, см. `Test Policy`).

## Test Policy

Структура тестов:

1. `tests/unit`
2. `tests/integration`
3. `tests/e2e`

Модель гейтов (по классу изменений):

1. `Fast gate` (`FE-only`    API ):
   - `python -m pytest tests/unit/test_frontend_contracts.py`,
   - `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py`.
2. `Targeted gate` (`FE + API slice`   backend-):
   -   `Fast gate`,
   - `python -m pytest tests/integration/test_frontend_dev_server.py`,
   -  e2e/   .
3. `Full gate` (крупный слайс, release-candidate, изменения evaluation/runtime/champion paths):
   - все из `Targeted gate`,
   - полный `python -m pytest`.

Полный прогон (для `Full gate`):

```powershell
python -m pytest
```

Прогон по уровням:

```powershell
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m e2e
```

Frontend-only :

```powershell
python -m pytest tests/unit/test_frontend_contracts.py
python -m pytest tests/e2e/test_frontend_shell_smoke_script.py
```

Важно для локальной проверки UI/API:

1. после изменений backend-ндпоинтов перезапускайте dev server;
2. проверяйте, что frontend proxy смотрит на актуальный backend instance, иначе возможны `404` на `/api/*`.

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

Decision CI- (deterministic,  8 , `hash_stable`):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --pretty
```

Decision LIVE- ( 8 ,    ):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_decision_v0.yaml --pretty
```

CI full-budget  ( dataset):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_full_v0.yaml --pretty
```

Live runtime full-budget  ( dataset,   ):

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_full_v0.yaml --pretty
```

Полный smoke-прогон arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena.ps1
```

Live smoke-прогон arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live.ps1
```

Decision smoke- arena (CI):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_decision.ps1
```

Decision live smoke- arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_decision.ps1
```

Full smoke- arena (CI full):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_full.ps1
```

Live full smoke- arena:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_arena_live_full.ps1
```

## Evaluation Profile Quickstart (PowerShell)

DSL target:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target dsl_runtime --pretty
```

Native target:

```powershell
python -m optimizer.evaluation.run_profile --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --target native_runtime --pretty
```

 (   2026-05-21):

1. canonical `stylizer_profile_ci_v0`    `native_runtime` (DSL->Native parity  demo-critical    `I4.S6a`).
2. preflight   fail-fast guard    source/binding  ( broken graph source  unresolved callable).
3. workaround policy `skip_unsupported` ; `I4.S8` , `V2.1.S3a` ,  delivery-  `V2.1.S3`.

Smoke- profile-driven path:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_evaluation_profile_native_preflight.ps1
```

DSL-vs-native parity harness ( CI-gate):

```powershell
python -m optimizer.parity.run --profile-file .\examples\profiles\stylizer_profile_ci_v0.yaml --cases-limit 1 --fail-on-mismatch --pretty
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_dsl_native_parity.ps1
```

## Evidence Pack Quickstart (PowerShell)

 evidence pack   CI arena-:

```powershell
python -m optimizer.evidence.generate_pack --arena-file .\examples\arena\support_tournament_ci_v0.yaml --out-dir .\tmp\evidence_pack --pretty
```

 evidence pack    arena JSON:

```powershell
python -m optimizer.arena.run_tournament --arena-file .\examples\arena\support_tournament_ci_v0.yaml --pretty | Out-File -LiteralPath .\tmp\arena_result.json -Encoding utf8
python -m optimizer.evidence.generate_pack --arena-result-file .\tmp\arena_result.json --out-dir .\tmp\evidence_pack --pretty
```

Smoke- evidence pack:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_generate_evidence_pack.ps1
```

## Champion Bundle Quickstart (PowerShell)

 champion bundle   CI decision arena-:

```powershell
python -m optimizer.champion.export_bundle --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --out-dir .\tmp\champion_bundle --bundle-name stylizer_ci_bundle --force --pretty
```

  :

1. `bundle_manifest.json` (`default_runtime_target=native_runtime`,  `default_entrypoint_file`  `legacy_debug_entrypoint_file`),
2. `parity_report.json` (`is_equivalent_agent=true`  `native_runtime_smoke.passed=true`),
3. `README.bundle.md`   bundle (native-first   ),
4. `native_agent\app\run.py` (standalone runtime entrypoint  `optimizer.*` ).

Smoke- champion bundle export:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_export_champion_bundle.ps1
```

## Frontend Shell Quickstart (PowerShell)

 React/TS  (    `frontend/src`):

```powershell
cd .\frontend
npm install
npm run build
cd ..
```

 capability shell (`C1..C6`):

```powershell
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

  :

```text
http://127.0.0.1:4173/
```

  frontend  backend:

1. Backend ( 1):

```powershell
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

2. Frontend Vite dev server ( 2):

```powershell
cd .\frontend
npm run dev
```

3.  frontend:

```text
http://127.0.0.1:5173/
```

  `/api`   :

1.   `5173`    URL  `/api/...`.
2. Vite proxy     Python backend `http://127.0.0.1:4173`.
3.   proxy  `/design_system/*`,     -    dev.

Smoke- frontend shell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_frontend_shell.ps1
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
3.   demo-      `OPENROUTER_MODEL` (   `.env.example`  `meta-llama/llama-3.1-8b-instruct`).
4.       full-       .

Важно: `.env` добавлен в `.gitignore` и не должен попадать в git.






