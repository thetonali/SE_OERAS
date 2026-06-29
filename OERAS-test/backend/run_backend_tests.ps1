param(
    [switch]$Coverage
)

$ErrorActionPreference = 'Stop'
$backendRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\ExamOnline')
Push-Location $backendRoot
try {
    if ($Coverage) {
        coverage run manage.py test user exam question record
        coverage report
        coverage html -d (Join-Path $PSScriptRoot '..\reports\backend-coverage')
    }
    else {
        python manage.py test user exam question record
    }
}
finally {
    Pop-Location
}
