@echo off
setlocal
title TerraEdge Arduino Setup
cd /d "%~dp0"
echo TerraEdge Arduino environment setup
echo Internet access is required. The process can take several minutes.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\Install-TerraEdgeArduino.ps1"
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" (echo Setup did not complete. Read setup\arduino-setup.log.) else (echo Setup completed. Both sketches compiled successfully.)
echo.
pause
exit /b %RESULT%
