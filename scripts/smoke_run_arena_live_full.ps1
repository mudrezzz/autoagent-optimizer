# Smoke-скрипт полного live-прогона stylizer-турнира по всему dataset (дороже и дольше).
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к full live arena-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_full_v0.yaml"

# Если модель явно не задана в окружении/`.env`, используем более дешевый дефолт для full live прогона.
if (-not $env:OPENROUTER_MODEL) {
    $env:OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct"
}

Write-Host "[SMOKE LIVE FULL] OPENROUTER_MODEL=$($env:OPENROUTER_MODEL)"
Write-Host "[SMOKE LIVE FULL] run stylizer architecture arena tournament (runtime, full budget)"
python -m optimizer.arena.run_tournament `
  --arena-file $arenaFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Arena live full smoke run failed"
}

Write-Host "[SMOKE LIVE FULL] stylizer arena runtime full tournament completed successfully."
