# Resume & Checkpoint Contract v0

## Purpose

`Resume & Checkpoint Contract v0` добавляет воспроизводимый путь `invoke -> checkpoint -> resume` для runtime workflow.

Ключевые модули:

1. [optimizer/renderer/langgraph_dai/checkpoint_store.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/checkpoint_store.py)
2. [optimizer/renderer/langgraph_dai/adapter.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/adapter.py)
3. [optimizer/renderer/langgraph_dai/run.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/renderer/langgraph_dai/run.py)

## Contract

1. `task_id` обязателен для checkpoint/resume сценария.
2. После `invoke` финальное состояние сохраняется в checkpoint-store по `task_id`.
3. `resume(task_id, payload_patch)`:
   - загружает checkpoint;
   - мерджит `payload_patch` в сохраненный payload;
   - выполняет `workflow.resume(...)`;
   - сохраняет обновленный checkpoint.

## CLI

Новый запуск:

```powershell
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\hitl_gate.yaml --payload-file .\tmp\payload_start.json --task-id resume-task-1 --checkpoint-dir .\tmp\runtime_checkpoints --pretty
```

Resume запуск:

```powershell
python -m optimizer.renderer.langgraph_dai.run --dsl-file .\examples\dsl\hitl_gate.yaml --resume-task-id resume-task-1 --payload-file .\tmp\payload_resume.json --checkpoint-dir .\tmp\runtime_checkpoints --pretty
```

## Negative Cases

1. Пустой `task_id` -> ошибка контракта.
2. `resume` по `task_id` без checkpoint -> ошибка.
3. Некорректный payload (не JSON-object) -> ошибка CLI.

