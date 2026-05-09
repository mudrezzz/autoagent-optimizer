# Smoke-скрипт profile-driven оценки (Evaluation Profile v0) на DSL target.
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и путь к CI profile-конфигу.
$repoRoot = Split-Path -Parent $PSScriptRoot
$profileFile = Join-Path $repoRoot "examples\profiles\stylizer_profile_ci_v0.yaml"

Write-Host "[SMOKE] run evaluation profile on dsl_runtime target"
python -m optimizer.evaluation.run_profile `
  --profile-file $profileFile `
  --target dsl_runtime `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Evaluation profile smoke run failed"
}

Write-Host "[SMOKE] evaluation profile run completed successfully."
