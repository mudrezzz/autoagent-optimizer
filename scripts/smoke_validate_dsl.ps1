# Скрипт запускает smoke-валидацию всех примеров DSL v0.
param()

$ErrorActionPreference = "Stop"

# Определяем корень репозитория относительно расположения скрипта.
$repoRoot = Split-Path -Parent $PSScriptRoot
$exampleDir = Join-Path $repoRoot "examples\dsl"

# Перебираем все YAML-файлы и валидируем их через CLI.
$files = Get-ChildItem -LiteralPath $exampleDir -Filter *.yaml | Sort-Object Name
if ($files.Count -eq 0) {
    throw "Не найдено DSL-примеров в $exampleDir"
}

foreach ($file in $files) {
    Write-Host "[SMOKE] validate $($file.FullName)"
    python -m optimizer.dsl.validate --file $file.FullName --pretty
    if ($LASTEXITCODE -ne 0) {
        throw "Валидация не прошла для $($file.FullName)"
    }
}

Write-Host "[SMOKE] DSL validation completed successfully."

