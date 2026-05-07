# Smoke-скрипт контрольного CI decision-прогона stylizer-турнира (8 кейсов, hash_stable).
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к decision CI arena-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_ci_decision_v0.yaml"

Write-Host "[SMOKE DECISION] run stylizer arena tournament (expected_stub, decision budget)"
python -m optimizer.arena.run_tournament `
  --arena-file $arenaFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Arena decision smoke run failed"
}

Write-Host "[SMOKE DECISION] stylizer decision tournament completed successfully."

