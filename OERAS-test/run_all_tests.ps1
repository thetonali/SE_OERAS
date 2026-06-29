$ErrorActionPreference = 'Stop'

Write-Host '== OERAS frontend tests =='
Push-Location (Join-Path $PSScriptRoot 'frontend')
try {
    npm run test:coverage
}
finally {
    Pop-Location
}

Write-Host '== OERAS backend tests =='
Push-Location (Join-Path $PSScriptRoot 'backend')
try {
    .\run_backend_tests.ps1
}
finally {
    Pop-Location
}
