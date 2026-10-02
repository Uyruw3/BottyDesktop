$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    python -m venv (Join-Path $root ".venv")
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the virtual environment."
    }
}

& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Could not upgrade pip."
}

& $venvPython -m pip install -e ".[dev,voice]"
if ($LASTEXITCODE -ne 0) {
    throw "Could not install Botty Desktop dependencies."
}

Write-Host "Installation complete. Run scripts\run.ps1 to start Botty."
