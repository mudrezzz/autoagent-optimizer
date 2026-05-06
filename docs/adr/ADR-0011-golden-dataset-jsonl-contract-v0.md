# ADR-0011: Golden Dataset JSONL Contract v0

- Status: Accepted
- Date: 2026-05-06
- Slice: I3.S1
- Decision Makers: Project team
- Supersedes: N/A

## Context

Для перехода к evaluation (`I3.S2`) и arena (`I3.S3`) нужна единая, проверяемая и простая форма тестовых кейсов.
Без явного контракта dataset-файлов сравнение архитектур будет нерепродуцируемым.

## Decision

Принять `Golden Dataset v0` в формате JSONL:

1. Одна строка = один кейс.
2. Обязательные поля: `case_id`, `input`, `expected`.
3. Дополнительные поля: `tags`, `metadata`.
4. Добавить typed loader и CLI-валидацию с диагностикой по строкам.

## Alternatives Considered

1. Хранить датасет в YAML.
2. Использовать один большой JSON-массив.
3. Оставить неструктурированный формат без schema-валидации.

## Consequences

### Positive

1. Dataset становится стабильным контрактом для evaluation.
2. Легко добавлять/ревьюить кейсы построчно.
3. Четкая диагностика ошибок загрузки по line number.

### Negative / Trade-offs

1. Нет строгой типизации содержимого `input/expected` на доменном уровне v0.
2. Для сложных мультимодальных кейсов контракт придется расширять в последующих версиях.

## Implementation Notes

1. Добавлены `dataset_schema`, `dataset_loader`, `validate_dataset` CLI.
2. Добавлен эталонный dataset `examples/datasets/golden_support_v1.jsonl`.
3. Добавлен smoke script и покрытие unit/integration/e2e.

## Verification

1. Unit: loader + duplicate/json/schema ошибки.
2. Integration: CLI success/failure.
3. E2E: smoke script проходит.
4. Полный `python -m pytest` зеленый.

## Links

1. `docs/specs/Golden_Dataset_v0.md`
2. `Roadmap.md` (I3.S1)
3. `docs/backlog/Executable_Slice_Backlog.md`

