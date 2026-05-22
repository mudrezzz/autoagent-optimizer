# Smoke runner for frontend capability shell (V2.1.S1).
param()

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"

$bindHost = "127.0.0.1"
$port = 4173
$baseUrl = "http://$bindHost`:$port"
$process = $null

try {
  Write-Host "[SMOKE] start frontend dev server"
  $process = Start-Process `
    -FilePath "python" `
    -ArgumentList @("-m", "optimizer.frontend.dev_server", "--host", $bindHost, "--port", "$port") `
    -WorkingDirectory $repoRoot `
    -WindowStyle Hidden `
    -PassThru

  Write-Host "[SMOKE] wait for health endpoint"
  $isReady = $false
  for ($i = 0; $i -lt 40; $i++) {
    try {
      $health = Invoke-RestMethod -Uri "$baseUrl/api/health" -Method Get -TimeoutSec 2
      if ($health.status -eq "ok") {
        $isReady = $true
        break
      }
    } catch {
      Start-Sleep -Milliseconds 250
    }
  }

  if (-not $isReady) {
    throw "Frontend dev server was not ready in time."
  }

  Write-Host "[SMOKE] verify capability catalog"
  $capabilities = Invoke-RestMethod -Uri "$baseUrl/api/capabilities" -Method Get -TimeoutSec 4
  if ($capabilities.capabilities.Count -ne 6) {
    throw "Capability catalog must contain 6 items."
  }

  Write-Host "[SMOKE] run real C1 validate+compile call"
  $payload = @{ dsl_file = "examples/dsl/style_direct_llm.yaml" } | ConvertTo-Json -Compress
  $c1 = Invoke-RestMethod -Uri "$baseUrl/api/c1/validate-compile" -Method Post -Body $payload -ContentType "application/json" -TimeoutSec 8
  if ($c1.status -ne "success") {
    throw "C1 endpoint returned non-success status."
  }

  Write-Host "[SMOKE] frontend capability shell completed successfully."
} finally {
  if ($null -ne $process -and -not $process.HasExited) {
    Stop-Process -Id $process.Id -Force
  }
}
