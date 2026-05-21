# Smoke-скрипт проверки, что native preflight пропускает профиль с `tool`-узлами после I4.S6.
param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$profileFile = Join-Path $repoRoot "tmp\native_tool_compatible_profile.yaml"
$datasetFile = Join-Path $repoRoot "examples\datasets\golden_support_v1.jsonl"
$dslOk = Join-Path $repoRoot "examples\dsl\direct_llm.yaml"
$dslTool = Join-Path $repoRoot "examples\dsl\ocr_first.yaml"
$profileYaml = @"
version: evaluation_profile_v0
profile_id: native_tool_compatible_profile_v0
task_type: mixed_native_preflight
supported_targets:
  - native_runtime
default_target: native_runtime
dataset_file: $datasetFile
evaluators:
  - evaluator_type: golden_oracle
    config: {}
    budget: {}
comparative_metrics:
  - metric_id: pass_rate
    direction: desc
    weight: 1.0
    source: golden_oracle
diagnostic_signals:
  - signal_id: diag_native
    stage_scope: validate
    aggregation: sum
participants:
  - participant_id: ok_candidate
    dsl_file: $dslOk
    stub_behavior: perfect
  - participant_id: tool_candidate
    dsl_file: $dslTool
    stub_behavior: fail_all
"@
Set-Content -LiteralPath $profileFile -Value $profileYaml -Encoding utf8

Write-Host "[SMOKE] run evaluation profile on native_runtime (expect preflight pass)"
$outFile = Join-Path $repoRoot "tmp\native_preflight_stdout.json"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outFile) | Out-Null
if (Test-Path -LiteralPath $outFile) {
  Remove-Item -LiteralPath $outFile -Force
}

python -m optimizer.evaluation.run_profile `
  --profile-file $profileFile `
  --target native_runtime `
  --pretty > $outFile

if ($LASTEXITCODE -ne 0) {
  throw "Expected successful native run for tool-compatible profile, but command failed."
}

$stdoutRaw = Get-Content -LiteralPath $outFile -Raw
if (-not ($stdoutRaw -match '"can_execute_native"\s*:\s*true')) {
  throw "Expected `can_execute_native=true` in native preflight response. stdout: $stdoutRaw"
}
if (-not ($stdoutRaw -match '"execution_mode"\s*:\s*"native_runtime"')) {
  throw "Expected `execution_mode=native_runtime` in run output. stdout: $stdoutRaw"
}

Write-Host "[SMOKE] native preflight pass behavior verified successfully."
