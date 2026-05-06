# AutoAgent Optimizer

OSS-first платформа для архитектурного поиска, white-box оценки и итеративной оптимизации compound AI systems.

## Current Status

- `Phase`: MVP-1 (foundation)
- `Iteration`: I3 - Evaluation + Arena Lite
- `Overall`: In Progress (I2.S1-I3.S1 done)
- `Next Slice`: I3.S2 Executable oracle runner (schema/pytest)

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
- `optimizer/evaluation` - golden dataset contract, loader и CLI-валидация.
- `examples/dsl` - эталонные YAML-спеки (`direct_llm`, `ocr_first`, `hitl_gate`).
- `examples/graph_ir` - эталонные Graph IR JSON-спеки.
- `examples/datasets` - эталонные golden dataset JSONL кейсы.
- `scripts/smoke_validate_dsl.ps1` - smoke-проверка всех DSL-примеров.
- `scripts/smoke_validate_graph_ir.ps1` - smoke-проверка всех Graph IR-примеров.
- `scripts/smoke_compile_dsl_to_ir.ps1` - smoke-компиляция DSL в IR.
- `scripts/smoke_run_runtime_demo.ps1` - smoke runtime-демо исполнения workflow.
- `scripts/smoke_generate_agent_code.ps1` - smoke-демо генерации и запуска кодового агента.
- `scripts/smoke_validate_dataset.ps1` - smoke-валидация golden dataset.

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

## PowerShell JSON Tip

Для CLI-команд, где передается JSON payload, в PowerShell используйте `--payload-file` как основной способ запуска.
Это исключает ошибки экранирования вида `unrecognized arguments`.

## Runtime Demo Quickstart (PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path .\tmp | Out-Null
'{"query":"Кратко опиши цель проекта"}' | Set-Content -LiteralPath .\tmp\runtime_payload.json -Encoding UTF8
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\direct_llm.yaml --payload-file .\tmp\runtime_payload.json --pretty
```

Полный smoke-прогон демо:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_run_runtime_demo.ps1
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
