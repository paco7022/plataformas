@echo off
setlocal
cd /d "%~dp0"
set "GAME_ENGINE=%~dp0tools\godot\Godot_v4.6.2-stable_win64.exe"
if exist "%GAME_ENGINE%" (
  start "Santuario de las Raices" "%GAME_ENGINE%" --path "%~dp0."
  exit /b
)
where godot >nul 2>nul
if not errorlevel 1 (
  start "Santuario de las Raices" godot --path "%~dp0."
  exit /b
)
echo Abre project.godot con Godot 4.3 o posterior y pulsa F6 o F5.
echo Descarga oficial: https://godotengine.org/download/windows/
pause
