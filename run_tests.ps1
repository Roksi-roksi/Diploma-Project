$OutputEncoding = [System.Text.Encoding]::UTF8

$results = "./allure-results"
$report = "./final-report"
$rep_history = "$report/history"
$temp_history = "$env:TEMP\allure_history_backup"

if (Test-Path $results) {
    Remove-Item -Recurse -Force $results -ErrorAction SilentlyContinue
}

if (Test-Path $rep_history) {
    if (Test-Path $temp_history) { Remove-Item -Recurse -Force $temp_history }
    New-Item -ItemType Directory -Force -Path $temp_history | Out-Null
    Copy-Item -Path "$rep_history\*" -Destination $temp_history -Force -ErrorAction SilentlyContinue
}

if (Test-Path $report) {
    Remove-Item -Recurse -Force $report -ErrorAction SilentlyContinue
}

try {
    python -m pytest --alluredir=$results
} catch {
    Write-Host "Pytest завершился с критической ошибкой, но мы пробуем собрать отчет..." -ForegroundColor Yellow
}

if (Test-Path $temp_history) {
    New-Item -ItemType Directory -Force -Path "$results/history" | Out-Null
    Copy-Item -Path "$temp_history\*" -Destination "$results/history" -Force
    Remove-Item -Recurse -Force $temp_history -ErrorAction SilentlyContinue
}

allure generate $results -o $report --clean

allure open $report