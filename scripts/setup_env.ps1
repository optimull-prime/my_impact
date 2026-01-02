param(
    [switch]$Recreate
)

$ErrorActionPreference = 'Stop'

$venvPath = Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '.venv' | Resolve-Path -ErrorAction SilentlyContinue
if (-not $venvPath) { $venvPath = Join-Path $PSScriptRoot '..' | Join-Path -ChildPath '.venv' }

if ($Recreate -and (Test-Path $venvPath)) {
    Write-Host "Removing existing venv at $venvPath" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $venvPath
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at .venv" -ForegroundColor Cyan
    python -m venv .venv
}

$python = Join-Path $venvPath 'Scripts' | Join-Path -ChildPath 'python.exe'
Write-Host "Using interpreter: $python" -ForegroundColor Cyan

& $python -m pip install --upgrade pip
& $python -m pip install -r (Join-Path $PSScriptRoot '..' | Join-Path -ChildPath 'requirements.txt')

Write-Host "Done. In VS Code, the interpreter is set to .venv." -ForegroundColor Green
