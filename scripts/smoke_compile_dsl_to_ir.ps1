# Скрипт выполняет smoke-компиляцию всех DSL примеров в Graph IR и валидирует результат.
param()

$ErrorActionPreference = "Stop"

# Определяем рабочие каталоги.
$repoRoot = Split-Path -Parent $PSScriptRoot
$dslExampleDir = Join-Path $repoRoot "examples\dsl"
$outDir = Join-Path $repoRoot "tmp\compiled_ir"

# Очищаем прошлые артефакты smoke-компиляции.
if (Test-Path -LiteralPath $outDir) {
    Remove-Item -LiteralPath $outDir -Recurse -Force
}
New-Item -ItemType Directory -Path $outDir | Out-Null

# Компилируем каждый DSL-файл в отдельный Graph IR JSON.
$dslFiles = Get-ChildItem -LiteralPath $dslExampleDir -Filter *.yaml | Sort-Object Name
if ($dslFiles.Count -eq 0) {
    throw "Не найдено DSL-примеров в $dslExampleDir"
}

foreach ($dslFile in $dslFiles) {
    $outFile = Join-Path $outDir ($dslFile.BaseName + ".ir.json")
    Write-Host "[SMOKE] compile $($dslFile.FullName) -> $outFile"
    python -m optimizer.dsl.compile --dsl-file $dslFile.FullName --output-ir-file $outFile --pretty
    if ($LASTEXITCODE -ne 0) {
        throw "Компиляция не прошла для $($dslFile.FullName)"
    }

    Write-Host "[SMOKE] validate compiled $outFile"
    python -m optimizer.graph_ir.validate --file $outFile --pretty
    if ($LASTEXITCODE -ne 0) {
        throw "Валидация скомпилированного IR не прошла: $outFile"
    }
}

Write-Host "[SMOKE] DSL -> IR compilation completed successfully."

