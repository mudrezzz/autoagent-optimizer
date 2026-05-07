# Smoke-скрипт исполняемой oracle-оценки.
param()

$ErrorActionPreference = "Stop"

# Вычисляем корень репозитория и пути к входным артефактам.
$repoRoot = Split-Path -Parent $PSScriptRoot
$datasetFile = Join-Path $repoRoot "examples\datasets\golden_linkedin_stylizer_v1.jsonl"
$dslFile = Join-Path $repoRoot "examples\dsl\style_direct_llm.yaml"

Write-Host "[SMOKE] run oracle on golden dataset"
python -m optimizer.evaluation.run_oracle `
  --dsl-file $dslFile `
  --dataset-file $datasetFile `
  --execution-mode expected_stub `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Oracle smoke run failed"
}

Write-Host "[SMOKE] oracle run completed successfully."
