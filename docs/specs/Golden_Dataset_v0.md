# Golden Dataset v0

## Purpose

`Golden Dataset v0` определяет минимальный контракт датасета для evaluation и дальнейшего oracle/arena прогона.

Ключевые модули:

1. [optimizer/evaluation/dataset_schema.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/evaluation/dataset_schema.py)
2. [optimizer/evaluation/dataset_loader.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/evaluation/dataset_loader.py)
3. [optimizer/evaluation/validate_dataset.py](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/optimizer/evaluation/validate_dataset.py)

## JSONL Record Contract

Каждая непустая строка JSONL должна быть объектом вида:

1. `case_id: str` (обязательный, уникальный в файле)
2. `input: object` (обязательный, непустой)
3. `expected: object` (обязательный, непустой)
4. `tags: string[]` (опционально)
5. `metadata: object` (опционально)

## Validation Rules

1. Файл должен существовать и читаться как UTF-8/UTF-8-SIG.
2. Каждая строка должна быть валидным JSON-объектом.
3. `case_id` не должен дублироваться.
4. Ошибки возвращаются с номером строки.

## CLI

```powershell
python -m optimizer.evaluation.validate_dataset --dataset-file .\examples\datasets\golden_support_v1.jsonl --pretty
```

Вывод:

1. `status` (`success|failure`)
2. `records_total`
3. `unique_case_ids`
4. `tags_total`
5. `issues_total`

## Smoke

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_validate_dataset.ps1
```

