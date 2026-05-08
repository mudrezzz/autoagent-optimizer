# Champion Export Bundle v0

## Purpose

`Champion Export Bundle v0` фиксирует лучший найденный кандидат турнира в переносимом наборе артефактов, чтобы:

1. быстро передать winner в эксплуатацию или в следующий optimization-цикл;
2. сохранить evidence и диагностику в едином reproducible пакете;
3. иметь runnable code артефакт без повторного ручного восстановления конфига.

## CLI

```powershell
python -m optimizer.champion.export_bundle --arena-file .\examples\arena\support_tournament_ci_decision_v0.yaml --out-dir .\tmp\champion_bundle --bundle-name stylizer_ci_bundle --force --pretty
```

Альтернатива по заранее сохраненному arena output:

```powershell
python -m optimizer.champion.export_bundle --arena-result-file .\tmp\arena_result.json --out-dir .\tmp\champion_bundle --bundle-name stylizer_ci_bundle --force --pretty
```

## Bundle Structure

```text
<out_dir>/<bundle_name>/
  arena_result.json
  bundle_manifest.json
  diagnostic_map.json
  parity_report.json
  README.bundle.md
  evidence_pack.json
  evidence_pack.md
  winner_graph_ir.json
  inputs/
    <arena_input_file>
  winner_source/
    <winner_dsl_or_graph_ir_file>
  generated_agent/
    run_generated_agent.py
    README.generated.md
    <winner_package_name>/
      __init__.py
      agent.py
      bindings.py
      graph_ir.json
  native_agent/
    app/
      run.py
      workflow.py
    prompts/
      prompts.json
    artifacts/
      source_graph_ir.json
    README.md
    requirements.txt
```

## Artifact Semantics

1. `arena_result.json`:
   - исходный результат турнира для полного воспроизведения ranking/winner.
2. `evidence_pack.json` + `evidence_pack.md`:
   - explainable comparative/diagnostic evidence между winner/challenger.
3. `diagnostic_map.json`:
   - приоритизированные точки оптимизации winner:
     - `winner_diagnostics`: bottleneck точки из `top_bottlenecks`,
     - `winner_stage_watch`: fallback-точки наблюдения для стабильного winner,
     - `comparison_diff`: cross-metric gaps, где winner уступает challenger.
4. `winner_graph_ir.json`:
   - нормализованный Graph IR winner (из DSL компиляции или прямого graph_ir источника).
5. `parity_report.json`:
   - автоматическая проверка эквивалентности `DSL path` и `generated code path`:
     - совпадение Graph IR,
     - структурный parity runtime (`executed_nodes`, `skipped_nodes`, `node_output_keys`, `errors`, `trace_nodes_total`).
   - проверка выполняется в `mock_llm_for_stability` режиме, чтобы исключить вариативность LLM текста.
6. `README.bundle.md`:
   - инструкция для разработчика: как запустить сгенерированного агента и как интерпретировать parity report.
7. `generated_agent/*`:
   - runnable кодовый артефакт winner (codegen-путь I2.S2).
8. `native_agent/*`:
   - standalone native runtime пакет на `langgraph-dai` без импортов `optimizer.*`.
9. `bundle_manifest.json`:
   - индекс всех файлов bundle и путь до entrypoint сгенерированного агента.

## Success Output Contract

CLI возвращает JSON:

```json
{
  "status": "success",
  "version": "champion_bundle_v0",
  "bundle_dir": "...",
  "winner_id": "...",
  "manifest_file": "...",
  "diagnostic_map_file": "...",
  "parity_report_file": "...",
  "bundle_readme_file": "...",
  "evidence_pack_json_file": "...",
  "evidence_pack_markdown_file": "...",
  "generated_agent_entrypoint_file": "...",
  "native_agent_entrypoint_file": "..."
}
```

## Verification

1. Unit:
   - `tests/unit/test_champion_diagnostic_map.py`
2. Integration:
   - `tests/integration/test_champion_export_bundle_cli.py`
3. E2E:
   - `tests/e2e/test_champion_export_bundle_smoke_script.py`
4. Smoke script:
   - `scripts/smoke_export_champion_bundle.ps1`
