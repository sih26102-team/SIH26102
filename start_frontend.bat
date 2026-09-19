@echo off
title CivicShield Frontend Launcher
echo ====================================================
echo Starting CivicShield Frontend using Portable Node.js
echo ====================================================

:: Force the command prompt to the exact directory where the bat file is
cd /d "%~dp0"

:: Set PATH to use the portable node ONLY for this script
set PATH=%~dp0node_portable\node-v20.11.1-win-x64;%PATH%

:: Verify Node works
echo Verifying Node.js...
node -v
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Node.js failed to run.
    pause
    exit /b
)

echo Changing to frontend directory...
cd frontend-dashboard
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Could not find frontend-dashboard folder!
    pause
    exit /b
)

echo.
echo Installing dependencies (this may take a minute the first time)...
call npm install
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: npm install failed!
    pause
    exit /b
)

echo.
echo Starting Vite development server...
call npm run dev
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: npm run dev failed!
)
pause
