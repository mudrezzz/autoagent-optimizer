# Скрипт выполняет smoke-валидацию всех референсных Graph IR примеров.
param()

$ErrorActionPreference = "Stop"

# Вычисляем путь до корня репозитория и каталога с примерами Graph IR.
$repoRoot = Split-Path -Parent $PSScriptRoot
$exampleDir = Join-Path $repoRoot "examples\graph_ir"

# Находим все JSON-файлы примеров и валидируем каждый через CLI.
$files = Get-ChildItem -LiteralPath $exampleDir -Filter *.json | Sort-Object Name
if ($files.Count -eq 0) {
    throw "Не найдено Graph IR примеров в $exampleDir"
}

foreach ($file in $files) {
    Write-Host "[SMOKE] validate $($file.FullName)"
    python -m optimizer.graph_ir.validate --file $file.FullName --pretty
    if ($LASTEXITCODE -ne 0) {
        throw "Валидация не прошла для $($file.FullName)"
    }
}

Write-Host "[SMOKE] Graph IR validation completed successfully."

