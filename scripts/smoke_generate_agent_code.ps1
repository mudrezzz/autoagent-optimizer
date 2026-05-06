# Smoke runner for generated agent code demo.
param()

$ErrorActionPreference = "Stop"

# Resolve repository root.
$repoRoot = Split-Path -Parent $PSScriptRoot
$tmpDir = Join-Path $repoRoot "tmp\generated_agent_demo"
if (Test-Path -LiteralPath $tmpDir) {
  Remove-Item -LiteralPath $tmpDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tmpDir | Out-Null

$payloadFile = Join-Path $tmpDir "payload.json"
'{"query":"Briefly describe project purpose."}' | Set-Content -LiteralPath $payloadFile -Encoding UTF8

Write-Host "[SMOKE] generate runtime agent from DSL"
python -m optimizer.codegen.generate `
  --dsl-file (Join-Path $repoRoot "examples\dsl\direct_llm.yaml") `
  --output-dir $tmpDir `
  --package-name "smoke_direct_agent" `
  --force `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Agent code generation failed"
}

Write-Host "[SMOKE] run generated agent"
python (Join-Path $tmpDir "run_generated_agent.py") `
  --payload-file $payloadFile `
  --pretty
if ($LASTEXITCODE -ne 0) {
    throw "Generated agent execution failed"
}

Write-Host "[SMOKE] generated agent code demo completed successfully."

