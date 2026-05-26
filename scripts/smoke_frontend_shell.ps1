# Smoke runner for frontend capability shell (V2.3.S7 / C1+C2+C3+C4+C5 vertical slice).
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
    throw "C1 capability must be enabled in V2.3.S7."
  }
  if ($c1.name -ne "Battle Registry") {
    throw "C1 capability name must match product capability model."
  }
  $c2 = $capabilities.capabilities | Where-Object { $_.id -eq "c2" }
  if ($null -eq $c2 -or $c2.status -ne "enabled") {
    throw "C2 capability must be enabled in V2.3.S7."
  }
  $c3 = $capabilities.capabilities | Where-Object { $_.id -eq "c3" }
  if ($null -eq $c3 -or $c3.status -ne "enabled") {
    throw "C3 capability must be enabled in V2.3.S7."
  }
  $c4 = $capabilities.capabilities | Where-Object { $_.id -eq "c4" }
  if ($null -eq $c4 -or $c4.status -ne "enabled") {
    throw "C4 capability must be enabled in V2.3.S7."
  }
  $c5 = $capabilities.capabilities | Where-Object { $_.id -eq "c5" }
  if ($null -eq $c5 -or $c5.status -ne "enabled") {
    throw "C5 capability must be enabled in V2.3.S7."
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

  Write-Host "[SMOKE] run C3 pattern flow"
  $selectionGet = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/patterns/selection" -Method Get -TimeoutSec 8
  if ($selectionGet.status -ne "success") {
    throw "C3 selection endpoint returned non-success status."
  }
  $selectionPayload = @{
    include_pattern_ids = @("style.pattern_cleaner")
    exclude_pattern_ids = @("style.hitl_reviewer")
  } | ConvertTo-Json -Compress
  $selectionPost = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/patterns/selection" -Method Post -Body $selectionPayload -ContentType "application/json" -TimeoutSec 8
  if ($selectionPost.status -ne "success") {
    throw "C3 update selection endpoint returned non-success status."
  }
  $patternSearch = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/patterns/search?q=rewrite&limit=5" -Method Get -TimeoutSec 8
  if ($patternSearch.status -ne "success" -or $patternSearch.returned -lt 1) {
    throw "C3 pattern search endpoint returned unexpected payload."
  }

  Write-Host "[SMOKE] run C4 dataset flow"
  $datasetCreatePayload = @{ name = "stylizer-dataset"; description = "Smoke dataset" } | ConvertTo-Json -Compress
  $datasetCreate = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/datasets/create" -Method Post -Body $datasetCreatePayload -ContentType "application/json" -TimeoutSec 8
  if ($datasetCreate.status -ne "success") {
    throw "C4 create dataset endpoint returned non-success status."
  }
  $datasetId = $datasetCreate.active_dataset_id

  $datasetAddRowPayload = @{
    row = @{
      case_id = "case_smoke_1"
      input = "input smoke"
      expected = "expected smoke"
      notes = "smoke"
    }
  } | ConvertTo-Json -Compress
  $datasetAddRow = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/datasets/$datasetId/rows/add" -Method Post -Body $datasetAddRowPayload -ContentType "application/json" -TimeoutSec 8
  if ($datasetAddRow.status -ne "success" -or $datasetAddRow.active_dataset.rows_total -lt 1) {
    throw "C4 add dataset row endpoint returned unexpected payload."
  }

  $datasetValidate = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/datasets/$datasetId/validate" -Method Post -Body "{}" -ContentType "application/json" -TimeoutSec 8
  if ($datasetValidate.status -ne "success" -or $datasetValidate.validation_report.rows_total -lt 1) {
    throw "C4 validate dataset endpoint returned unexpected payload."
  }

  $datasetSaveVersionPayload = @{ label = "smoke-v1"; source = "manual" } | ConvertTo-Json -Compress
  $datasetSaveVersion = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/datasets/$datasetId/save-version" -Method Post -Body $datasetSaveVersionPayload -ContentType "application/json" -TimeoutSec 8
  if ($datasetSaveVersion.status -ne "success" -or $datasetSaveVersion.version.label -ne "smoke-v1") {
    throw "C4 save version endpoint returned unexpected payload."
  }

  $datasetAssignPayload = @{ dataset_ids = @($datasetId) } | ConvertTo-Json -Compress
  $datasetAssign = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/datasets/assign" -Method Post -Body $datasetAssignPayload -ContentType "application/json" -TimeoutSec 8
  if ($datasetAssign.status -ne "success" -or $datasetAssign.assigned_dataset_ids.Count -ne 1) {
    throw "C4 assign datasets endpoint returned unexpected payload."
  }

  $evalState = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/evaluation/state" -Method Get -TimeoutSec 8
  if ($evalState.status -ne "success" -or $evalState.comparative_metrics.Count -lt 1) {
    throw "C4 evaluation state endpoint returned unexpected payload."
  }

  $evalMetricsPayload = @{
    comparative_metrics = @(
      @{ metric_id = "quality_f1"; title = "Quality F1@K"; description = "quality"; enabled = $true; weight = 0.7 },
      @{ metric_id = "cost_per_case"; title = "Cost / case"; description = "cost"; enabled = $true; weight = 0.3 }
    )
    diagnostic_signals = @(
      @{ signal_id = "retrieval_coverage"; title = "Retrieval coverage"; description = "retrieval"; enabled = $true }
    )
  } | ConvertTo-Json -Compress
  $evalMetrics = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/evaluation/metrics/save" -Method Post -Body $evalMetricsPayload -ContentType "application/json" -TimeoutSec 8
  if ($evalMetrics.status -ne "success") {
    throw "C4 evaluation metrics save endpoint returned unexpected payload."
  }

  $evalEvaluatorsPayload = @{
    evaluators = @(
      @{ evaluator_id = "golden_oracle"; title = "Golden dataset oracle"; description = "deterministic"; enabled = $true },
      @{ evaluator_id = "llm_judge"; title = "LLM as a judge"; description = "semantic"; enabled = $true }
    )
  } | ConvertTo-Json -Compress
  $evalEvaluators = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/evaluation/evaluators/save" -Method Post -Body $evalEvaluatorsPayload -ContentType "application/json" -TimeoutSec 8
  if ($evalEvaluators.status -ne "success") {
    throw "C4 evaluation evaluators save endpoint returned unexpected payload."
  }

  $evalBudgetPayload = @{ budget = @{ max_cases = 12; max_llm_calls = 40; max_cost_usd = 1.5 } } | ConvertTo-Json -Compress
  $evalBudget = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/evaluation/budget/save" -Method Post -Body $evalBudgetPayload -ContentType "application/json" -TimeoutSec 8
  if ($evalBudget.status -ne "success" -or $evalBudget.budget.max_cases -ne 12) {
    throw "C4 evaluation budget save endpoint returned unexpected payload."
  }

  $evalValidate = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/evaluation/validate" -Method Post -Body "{}" -ContentType "application/json" -TimeoutSec 8
  if ($evalValidate.status -ne "success") {
    throw "C4 evaluation validate endpoint returned unexpected payload."
  }

  $evalVersionPayload = @{ label = "eval-smoke-v1"; source = "manual" } | ConvertTo-Json -Compress
  $evalVersion = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/evaluation/save-version" -Method Post -Body $evalVersionPayload -ContentType "application/json" -TimeoutSec 8
  if ($evalVersion.status -ne "success" -or $evalVersion.version.label -ne "eval-smoke-v1") {
    throw "C4 evaluation save version endpoint returned unexpected payload."
  }

  Write-Host "[SMOKE] run C5 optimizer setup flow"
  $optimizerState = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/optimizer/state" -Method Get -TimeoutSec 8
  if ($optimizerState.status -ne "success" -or $optimizerState.methods.Count -lt 1) {
    throw "C5 optimizer state endpoint returned unexpected payload."
  }

  $optimizerSavePayload = @{
    methods = @(
      @{ method_id = "random_search"; title = "Random search"; description = "baseline"; enabled = $true },
      @{ method_id = "grid_search"; title = "Grid search"; description = "deterministic"; enabled = $true }
    )
    controls = @(
      @{ control_id = "tune_prompts"; title = "Tune prompts"; description = "scope"; enabled = $true },
      @{ control_id = "tune_pattern_mix"; title = "Tune pattern mix"; description = "scope"; enabled = $true }
    )
    run_plan = @{ epochs_total = 3; candidates_per_epoch = 4; max_parallel_trials = 2; early_stop_patience = 1 }
    budget = @{ max_cases = 24; max_llm_calls = 200; max_cost_usd = 8.0; max_runtime_minutes = 30 }
  } | ConvertTo-Json -Compress
  $optimizerSave = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/optimizer/save" -Method Post -Body $optimizerSavePayload -ContentType "application/json" -TimeoutSec 8
  if ($optimizerSave.status -ne "success" -or $optimizerSave.run_plan.epochs_total -ne 3) {
    throw "C5 optimizer save endpoint returned unexpected payload."
  }

  $optimizerValidate = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/optimizer/validate" -Method Post -Body "{}" -ContentType "application/json" -TimeoutSec 8
  if ($optimizerValidate.status -ne "success") {
    throw "C5 optimizer validate endpoint returned unexpected payload."
  }

  $optimizerVersionPayload = @{ label = "opt-smoke-v1"; source = "manual" } | ConvertTo-Json -Compress
  $optimizerVersion = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/optimizer/save-version" -Method Post -Body $optimizerVersionPayload -ContentType "application/json" -TimeoutSec 8
  if ($optimizerVersion.status -ne "success" -or $optimizerVersion.version.label -ne "opt-smoke-v1") {
    throw "C5 optimizer save version endpoint returned unexpected payload."
  }

  $candidateId = $chatResult.candidate_set_draft.candidates[0].candidate_id
  $selectForTestsPayload = @{
    candidate_ids = @($candidateId)
    max_compile_attempts = 3
  } | ConvertTo-Json -Compress
  $selectForTests = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/candidates/select-for-tests" -Method Post -Body $selectForTestsPayload -ContentType "application/json" -TimeoutSec 8
  if ($selectForTests.status -ne "success") {
    throw "C2 select-for-tests endpoint returned unexpected payload."
  }

  $optimizerLaunchPayload = @{ triggered_by = "smoke_script" } | ConvertTo-Json -Compress
  $optimizerLaunch = Invoke-RestMethod -Uri "$baseUrl/api/arenas/$arenaId/optimizer/launch" -Method Post -Body $optimizerLaunchPayload -ContentType "application/json" -TimeoutSec 8
  if ($optimizerLaunch.status -ne "success" -or $optimizerLaunch.run.status -ne "queued") {
    throw "C5 optimizer launch endpoint returned unexpected payload."
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





