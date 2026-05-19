# Smoke-скрипт проверки preflight-блокировки native target на несовместимом профиле.
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к canonical stylizer profile.
$repoRoot = Split-Path -Parent $PSScriptRoot
$profileFile = Join-Path $repoRoot "examples\profiles\stylizer_profile_ci_v0.yaml"

Write-Host "[SMOKE] run evaluation profile on native_runtime (expect preflight fail)"
$stderrFile = Join-Path $repoRoot "tmp\native_preflight_stderr.json"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $stderrFile) | Out-Null
if (Test-Path -LiteralPath $stderrFile) {
  Remove-Item -LiteralPath $stderrFile -Force
}

$previousErrorPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
python -m optimizer.evaluation.run_profile `
  --profile-file $profileFile `
  --target native_runtime `
  --pretty 2> $stderrFile
$ErrorActionPreference = $previousErrorPreference

if ($LASTEXITCODE -eq 0) {
  throw "Expected preflight failure for incompatible native profile, but command succeeded."
}

$stderrRaw = Get-Content -LiteralPath $stderrFile -Raw
if (-not ($stderrRaw -match '"error_type"\s*:\s*"native_compatibility_preflight_failed"')) {
  throw "Unexpected stderr payload for native preflight failure. stderr: $stderrRaw"
}
if (-not ($stderrRaw -match '"can_execute_native"\s*:\s*false')) {
  throw "Expected `can_execute_native=false` in native preflight response. stderr: $stderrRaw"
}

Write-Host "[SMOKE] native preflight blocking behavior verified successfully."
