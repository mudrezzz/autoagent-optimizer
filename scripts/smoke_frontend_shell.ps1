# Smoke runner for frontend capability shell (V2.3.S1 / C1 vertical slice).
param()

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"

$storeFile = Join-Path $repoRoot "tmp\tests\smoke_frontend_workspace_registry.json"
New-Item -ItemType Directory -Path (Split-Path -Parent $storeFile) -Force | Out-Null
if (Test-Path -LiteralPath $storeFile) {
  Remove-Item -LiteralPath $storeFile -Force
}

$bindHost = "127.0.0.1"

function Get-FreeTcpPort {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), 0)
  $listener.Start()
  try {
    return $listener.LocalEndpoint.Port
  } finally {
    $listener.Stop()
  }
}

$port = Get-FreeTcpPort
$baseUrl = "http://$bindHost`:$port"
$process = $null

try {
  Write-Host "[SMOKE] start frontend dev server"
  $env:AUTOAGENT_WORKSPACE_STORE_FILE = $storeFile
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

  $c1 = $capabilities.capabilities | Where-Object { $_.id -eq "c1" }
  if ($null -eq $c1 -or $c1.status -ne "enabled") {
    throw "C1 capability must be enabled in V2.3.S1."
  }
  if ($c1.name -ne "Workspace & Projects") {
    throw "C1 capability name must match product capability model."
  }

  Write-Host "[SMOKE] run C1 workspace/project flow"
  $workspacePayload = @{ name = "support-qa"; description = "Smoke workspace" } | ConvertTo-Json -Compress
  $workspaceResult = Invoke-RestMethod -Uri "$baseUrl/api/workspaces" -Method Post -Body $workspacePayload -ContentType "application/json" -TimeoutSec 8
  if ($workspaceResult.status -ne "success") {
    throw "Workspace create endpoint returned non-success status."
  }
  $workspaceId = $workspaceResult.workspace.workspace_id

  $projectPayload = @{ name = "support-qa.v1"; description = "Smoke project" } | ConvertTo-Json -Compress
  $projectResult = Invoke-RestMethod -Uri "$baseUrl/api/workspaces/$workspaceId/projects" -Method Post -Body $projectPayload -ContentType "application/json" -TimeoutSec 8
  if ($projectResult.status -ne "success") {
    throw "Project create endpoint returned non-success status."
  }
  $projectId = $projectResult.project.project_id

  $projectGet = Invoke-RestMethod -Uri "$baseUrl/api/projects/$projectId" -Method Get -TimeoutSec 8
  if ($projectGet.status -ne "success" -or $projectGet.project.project_id -ne $projectId) {
    throw "Project get endpoint returned unexpected payload."
  }

  Write-Host "[SMOKE] frontend capability shell completed successfully."
} finally {
  if ($null -ne $process -and -not $process.HasExited) {
    Stop-Process -Id $process.Id -Force
  }
  if (Test-Path -LiteralPath $storeFile) {
    Remove-Item -LiteralPath $storeFile -Force
  }
  Remove-Item Env:AUTOAGENT_WORKSPACE_STORE_FILE -ErrorAction SilentlyContinue
}
