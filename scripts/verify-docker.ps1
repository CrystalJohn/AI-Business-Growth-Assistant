$ErrorActionPreference = "Continue"
$env:DOCKER_BUILDKIT = "1"

Write-Host "`n=== Docker Optimization Verification ===" -ForegroundColor Cyan

Write-Host "`n[1] Image sizes:" -ForegroundColor Yellow
docker images --format "{{.Repository}}`t{{.Size}}" | Select-String -Pattern "ai_business|hr-chatbi"

Write-Host "`n[2] Container status:" -ForegroundColor Yellow
docker-compose ps -a

Write-Host "`n[3] Non-root verification:" -ForegroundColor Yellow
$apiId = docker-compose exec -T api id 2>$null
$webId = docker-compose exec -T web id 2>$null
Write-Host "  api: $apiId"
Write-Host "  web: $webId"
if ($apiId -match "uid=1001" -and $webId -match "uid=1001") {
    Write-Host "  PASS" -ForegroundColor Green
} else {
    Write-Host "  FAIL" -ForegroundColor Red
}

Write-Host "`n[4] Health endpoint:" -ForegroundColor Yellow
try {
    $h = (Invoke-RestMethod http://localhost:8000/health)
    if ($h.status -eq "ok" -and $h.db -eq "ok") {
        Write-Host "  PASS - status=$($h.status), db=$($h.db)" -ForegroundColor Green
    } else { Write-Host "  FAIL - $h" -ForegroundColor Red }
} catch { Write-Host "  FAIL - $_" -ForegroundColor Red }

Write-Host "`n[5] Schema HR check:" -ForegroundColor Yellow
try {
    $s = (Invoke-RestMethod http://localhost:8000/schema)
    $hasEmployees = $s.tables | Where-Object { $_.name -eq "employees" }
    $hasCustomers = $s.tables | Where-Object { $_.name -eq "customers" }
    if ($hasEmployees -and -not $hasCustomers) {
        Write-Host "  PASS - HR tables present, no business leftover" -ForegroundColor Green
    } else { Write-Host "  FAIL" -ForegroundColor Red }
} catch { Write-Host "  FAIL - $_" -ForegroundColor Red }

Write-Host "`n[6] DB seed:" -ForegroundColor Yellow
$count = docker-compose exec -T postgres psql -U admin -d bizgrowth -t -c "SELECT COUNT(*) FROM employees;" 2>$null
Write-Host "  employees count: $($count.Trim())"
if ($count.Trim() -eq "150") { Write-Host "  PASS" -ForegroundColor Green } else { Write-Host "  FAIL" -ForegroundColor Red }

Write-Host "`n[7] api-migrate status:" -ForegroundColor Yellow
$migrateState = docker inspect --format='{{.State.Status}} ({{.State.ExitCode}})' (docker-compose ps -aq api-migrate) 2>$null
Write-Host "  $migrateState"
if ($migrateState -match "exited \(0\)") { Write-Host "  PASS" -ForegroundColor Green } else { Write-Host "  FAIL" -ForegroundColor Red }

Write-Host "`n=== Verification complete ===" -ForegroundColor Cyan