# Smoke runner for golden dataset validation.
param()

$ErrorActionPreference = "Stop"

# Resolve repository root.
$repoRoot = Split-Path -Parent $PSScriptRoot
$datasetFile = Join-Path $repoRoot "examples\datasets\golden_support_v1.jsonl"

Write-Host "[SMOKE] validate golden dataset"
python -m optimizer.evaluation.validate_dataset `
  --dataset-file $datasetFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Golden dataset validation failed"
}

Write-Host "[SMOKE] golden dataset validation completed successfully."

