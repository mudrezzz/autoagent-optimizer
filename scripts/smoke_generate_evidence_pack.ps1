# Smoke-скрипт генерации Evidence Pack v0 по стабильному CI arena-конфигу.
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория, путь до CI-конфига arena и каталог артефактов.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_ci_v0.yaml"
$outDir = Join-Path $repoRoot "tmp\evidence_pack_smoke"

Write-Host "[SMOKE] generate evidence pack from arena tournament"
python -m optimizer.evidence.generate_pack `
  --arena-file $arenaFile `
  --out-dir $outDir `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Evidence pack smoke generation failed"
}

Write-Host "[SMOKE] evidence pack generation completed successfully."

