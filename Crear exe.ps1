$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$gamePython = Join-Path $PSScriptRoot 'pygame_version\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $gamePython)) {
    throw 'Ejecuta primero Instalar requisitos Pygame.cmd.'
}
& $gamePython -m pip install -r pygame_version/requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las herramientas de compilacion.' }
$gameBackground = Join-Path $PSScriptRoot 'assets\sanctuary.png'
& $gamePython -m PyInstaller --noconfirm --clean --onefile --windowed --name SantuarioDeLasRaices --distpath releases --workpath build --specpath build --add-data "${gameBackground}:assets" pygame_version/main.py
if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar el ejecutable.' }
Write-Host 'Listo: releases\SantuarioDeLasRaices.exe'
