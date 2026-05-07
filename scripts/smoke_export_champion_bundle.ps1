# Smoke-скрипт экспорта Champion Bundle v0 по стабильному CI Arena-конфигу.
param()

$ErrorActionPreference = "Stop"

# Вычисляем путь до корня репозитория и основных входных/выходных артефактов smoke запуска.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_ci_decision_v0.yaml"
$outDir = Join-Path $repoRoot "tmp\champion_bundle_smoke"
$bundleName = "stylizer_ci_bundle"

Write-Host "[SMOKE] export champion bundle from arena tournament"
python -m optimizer.champion.export_bundle `
  --arena-file $arenaFile `
  --out-dir $outDir `
  --bundle-name $bundleName `
  --force `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Champion bundle smoke export failed"
}

Write-Host "[SMOKE] champion bundle export completed successfully."

