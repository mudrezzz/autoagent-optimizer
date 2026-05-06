# Smoke-скрипт турнира Architecture Arena.
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к стабильному CI arena-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_ci_v0.yaml"

Write-Host "[SMOKE] run architecture arena tournament"
python -m optimizer.arena.run_tournament `
  --arena-file $arenaFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Arena smoke run failed"
}

Write-Host "[SMOKE] arena tournament completed successfully."
