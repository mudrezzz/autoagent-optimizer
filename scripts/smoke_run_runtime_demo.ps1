# Smoke runner for runtime renderer demos.
param()

$ErrorActionPreference = "Stop"

# Resolve repository root.
$repoRoot = Split-Path -Parent $PSScriptRoot
$tmpDir = Join-Path $repoRoot "tmp\runtime_demo"
if (Test-Path -LiteralPath $tmpDir) {
  Remove-Item -LiteralPath $tmpDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tmpDir | Out-Null

$payloadDirect = Join-Path $tmpDir "payload_direct.json"
$payloadLow = Join-Path $tmpDir "payload_low.json"
$payloadHigh = Join-Path $tmpDir "payload_high.json"
$payloadResume = Join-Path $tmpDir "payload_resume.json"
$checkpointDir = Join-Path $tmpDir "checkpoints"

'{"draft_post":"In todays world it is important to optimize writing quality. Lets review how to rewrite a post with the same facts but more human tone."}' | Set-Content -LiteralPath $payloadDirect -Encoding UTF8
'{"query":"Create safe ticket","action_risk":"low"}' | Set-Content -LiteralPath $payloadLow -Encoding UTF8
'{"query":"Execute risky action","action_risk":"high","review_decision":"approve"}' | Set-Content -LiteralPath $payloadHigh -Encoding UTF8
'{"action_risk":"high","review_decision":"approve"}' | Set-Content -LiteralPath $payloadResume -Encoding UTF8

Write-Host "[SMOKE] run style_direct_llm demo"
python -m optimizer.renderer.langgraph_dai.run `
  --dsl-file (Join-Path $repoRoot "examples\dsl\style_direct_llm.yaml") `
  --payload-file $payloadDirect `
  --pretty | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Runtime demo style_direct_llm failed"
}

Write-Host "[SMOKE] run hitl_gate demo with low risk branch"
python -m optimizer.renderer.langgraph_dai.run `
  --dsl-file (Join-Path $repoRoot "examples\dsl\hitl_gate.yaml") `
  --payload-file $payloadLow `
  --pretty | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Runtime demo hitl_gate low-risk failed"
}

Write-Host "[SMOKE] run hitl_gate demo with high risk branch"
python -m optimizer.renderer.langgraph_dai.run `
  --dsl-file (Join-Path $repoRoot "examples\dsl\hitl_gate.yaml") `
  --payload-file $payloadHigh `
  --pretty | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Runtime demo hitl_gate high-risk failed"
}

Write-Host "[SMOKE] run checkpoint invoke/resume contract"
python -m optimizer.renderer.langgraph_dai.run `
  --dsl-file (Join-Path $repoRoot "examples\dsl\hitl_gate.yaml") `
  --payload-file $payloadLow `
  --task-id "smoke-resume-task" `
  --checkpoint-dir $checkpointDir `
  --pretty | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Runtime demo resume invoke phase failed"
}

python -m optimizer.renderer.langgraph_dai.run `
  --dsl-file (Join-Path $repoRoot "examples\dsl\hitl_gate.yaml") `
  --resume-task-id "smoke-resume-task" `
  --payload-file $payloadResume `
  --checkpoint-dir $checkpointDir `
  --pretty | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Runtime demo resume phase failed"
}

Write-Host "[SMOKE] runtime renderer demo completed successfully."
