# Smoke runner for frontend capability shell (V2.3.S2 / C1+C2 vertical slice).
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
    throw "C1 capability must be enabled in V2.3.S2."
  }
  if ($c1.name -ne "Battle Registry") {
    throw "C1 capability name must match product capability model."
  }
  $c2 = $capabilities.capabilities | Where-Object { $_.id -eq "c2" }
  if ($null -eq $c2 -or $c2.status -ne "enabled") {
    throw "C2 capability must be enabled in V2.3.S2."
  }

  Write-Host "[SMOKE] run C1 battle flow"
  $arenaPayload = @{ name = "support-qa"; description = "Smoke battle" } | ConvertTo-Json -Compress
  $arenaResult = Invoke-RestMethod -Uri "$baseUrl/api/arenas" -Method Post -Body $arenaPayload -ContentType "application/json" -TimeoutSec 8
  if ($arenaResult.status -ne "success") {
    throw "Arena create endpoint returned non-success status."
  }
  $arenaId = $arenaResult.arena.workspace_id

  $arenaGet = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId" -Method Get -TimeoutSec 8
  if ($arenaGet.status -ne "success" -or $arenaGet.arena.workspace_id -ne $arenaId) {
    throw "Arena get endpoint returned unexpected payload."
  }

  Write-Host "[SMOKE] run C2 chat flow"
  $chatPayload = @{
    message = "Сделай пост для LinkedIn более человечным и менее шаблонным"
    generate_candidates = $true
    max_candidates = 3
  } | ConvertTo-Json -Compress
  $chatResult = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/chat/messages" -Method Post -Body $chatPayload -ContentType "application/json" -TimeoutSec 8
  if ($chatResult.status -ne "success") {
    throw "C2 chat message endpoint returned non-success status."
  }
  if ($null -eq $chatResult.candidate_set_draft -or $chatResult.candidate_set_draft.total -lt 1) {
    throw "C2 candidate draft was not generated."
  }

  $chatState = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/chat/state" -Method Get -TimeoutSec 8
  if ($chatState.status -ne "success" -or $chatState.messages_total -lt 2) {
    throw "C2 chat state endpoint returned unexpected payload."
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
