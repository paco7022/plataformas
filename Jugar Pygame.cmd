@echo off
setlocal
cd /d "%~dp0"
set "GAME_PYTHON=%~dp0pygame_version\.venv\Scripts\python.exe"
if not exist "%GAME_PYTHON%" (
    echo Falta el entorno del juego.
    echo Abre "Instalar requisitos Pygame.cmd" y vuelve a intentarlo.
    pause
    exit /b 1
)
"%GAME_PYTHON%" -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo Hay que reparar las dependencias del juego.
    echo Abre "Instalar requisitos Pygame.cmd" y vuelve a intentarlo.
    pause
    exit /b 1
)
"%GAME_PYTHON%" -X "pycache_prefix=%~dp0pygame_version\.venv\cache" pygame_version/main.py
if errorlevel 1 (
    pause
    exit /b 1
)
