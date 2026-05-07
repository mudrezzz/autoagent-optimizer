# Smoke-скрипт decision live-прогона stylizer-турнира (8 кейсов, quality-модель).
param()

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

# Вычисляем корень репозитория и путь к decision live arena-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_decision_v0.yaml"

# Для decision-прогона по умолчанию используем более сильную модель, если не задано иное.
if (-not $env:OPENROUTER_MODEL) {
    $env:OPENROUTER_MODEL = "openai/gpt-4o-mini"
}

Write-Host "[SMOKE LIVE DECISION] OPENROUTER_MODEL=$($env:OPENROUTER_MODEL)"
Write-Host "[SMOKE LIVE DECISION] run stylizer arena tournament (runtime, decision budget)"
python -m optimizer.arena.run_tournament `
  --arena-file $arenaFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Arena live decision smoke run failed"
}

Write-Host "[SMOKE LIVE DECISION] stylizer live decision tournament completed successfully."

