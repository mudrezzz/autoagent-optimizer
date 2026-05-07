# Smoke-скрипт live-режима турнира stylizer-кейса (runtime + LLM).
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к live arena-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_v0.yaml"

# Если модель явно не задана в окружении/`.env`, используем более дешевый дефолт для smoke-live прогона.
if (-not $env:OPENROUTER_MODEL) {
    $env:OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct"
}

Write-Host "[SMOKE LIVE] OPENROUTER_MODEL=$($env:OPENROUTER_MODEL)"
Write-Host "[SMOKE LIVE] run stylizer architecture arena tournament (runtime)"
python -m optimizer.arena.run_tournament `
  --arena-file $arenaFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Arena live smoke run failed"
}

Write-Host "[SMOKE LIVE] stylizer arena runtime tournament completed successfully."
