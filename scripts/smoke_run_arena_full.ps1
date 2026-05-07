# Smoke-скрипт полного CI-турнира (expected_stub) по всему stylizer dataset.
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к full CI arena-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_ci_full_v0.yaml"

Write-Host "[SMOKE FULL] run stylizer architecture arena tournament (expected_stub, full budget)"
python -m optimizer.arena.run_tournament `
  --arena-file $arenaFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Arena full smoke run failed"
}

Write-Host "[SMOKE FULL] stylizer arena full tournament completed successfully."
