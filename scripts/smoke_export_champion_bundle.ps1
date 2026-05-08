# Smoke-скрипт экспорта Champion Bundle v0 по стабильному CI Arena-конфигу.
param()

$ErrorActionPreference = "Stop"

# Вычисляем путь до корня репозитория и основных входных/выходных артефактов smoke запуска.
$repoRoot = Split-Path -Parent $PSScriptRoot
$arenaFile = Join-Path $repoRoot "examples\arena\support_tournament_ci_decision_v0.yaml"
$outDir = Join-Path $repoRoot "tmp\champion_bundle_smoke"
$bundleName = "stylizer_ci_bundle"
$bundleDir = Join-Path $outDir $bundleName
$nativeRunner = Join-Path $bundleDir "native_agent\app\run.py"
$nativeAgentDir = Join-Path $bundleDir "native_agent"
$nativePayload = Join-Path $repoRoot "tmp\native_bundle_payload.json"

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

# Проверяем standalone native runtime артефакт из bundle.
'{"draft_post":"Проверка standalone native runtime из champion bundle."}' | Set-Content -LiteralPath $nativePayload -Encoding UTF8
Write-Host "[SMOKE] run standalone native agent from exported bundle"
$currentDir = Get-Location
Set-Location $nativeAgentDir
python $nativeRunner `
  --payload-file $nativePayload `
  --pretty
$nativeExit = $LASTEXITCODE
Set-Location $currentDir
if ($nativeExit -ne 0) {
    throw "Standalone native agent smoke run failed"
}

Write-Host "[SMOKE] champion bundle export completed successfully."
