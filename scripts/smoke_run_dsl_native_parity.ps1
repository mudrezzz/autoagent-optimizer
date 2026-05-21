# Smoke-скрипт DSL-vs-native parity harness с CI-gate режимом.
param()

$ErrorActionPreference = "Stop"

# Вычисляем путь до корня репозитория и файлов артефактов smoke-запуска.
$repoRoot = Split-Path -Parent $PSScriptRoot
$profileFile = Join-Path $repoRoot "examples\profiles\stylizer_profile_ci_v0.yaml"
$outFile = Join-Path $repoRoot "tmp\parity\stylizer_parity_report.json"

Write-Host "[SMOKE] run DSL-vs-native parity harness"
python -m optimizer.parity.run `
  --profile-file $profileFile `
  --cases-limit 1 `
  --out-file $outFile `
  --fail-on-mismatch `
  --pretty
if ($LASTEXITCODE -ne 0) {
  throw "Parity harness smoke run failed."
}

$reportRaw = Get-Content -LiteralPath $outFile -Raw
if (-not ($reportRaw -match '"passed"\s*:\s*true')) {
  throw "Expected `passed=true` in parity report. report: $reportRaw"
}

Write-Host "[SMOKE] DSL-vs-native parity harness completed successfully."

