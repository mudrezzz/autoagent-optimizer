# Smoke-скрипт live-режима турнира stylizer-кейса (runtime + LLM).
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к live arena-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_v0.yaml"

Write-Host "[SMOKE LIVE] run stylizer architecture arena tournament (runtime)"
python -m optimizer.arena.run_tournament `
  --arena-file $arenaFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Arena live smoke run failed"
}

Write-Host "[SMOKE LIVE] stylizer arena runtime tournament completed successfully."
