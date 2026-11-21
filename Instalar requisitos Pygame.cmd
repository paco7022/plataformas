@echo off
setlocal
cd /d "%~dp0"
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo Instalando Python 3.12...
    py install --yes 3.12
    if errorlevel 1 goto error
)
if not exist "pygame_version\.venv\Scripts\python.exe" (
    py -3.12 -m venv "pygame_version\.venv"
    if errorlevel 1 goto error
)
"pygame_version\.venv\Scripts\python.exe" -m pip install -r "pygame_version\requirements.txt"
if errorlevel 1 goto error
"pygame_version\.venv\Scripts\python.exe" -m pip check
if errorlevel 1 goto error
echo.
echo Listo. Abre "Jugar Pygame.cmd" para jugar.
pause
exit /b 0

:error
echo.
echo No se pudo completar la instalacion. Revisa el error anterior.
echo Si falta el comando py, instala Python 3.12 desde https://www.python.org/downloads/windows/
pause
exit /b 1
