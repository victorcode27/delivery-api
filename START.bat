@echo off
title Delivery Manifest System - Launcher

echo ============================================
echo    Delivery Manifest System
echo ============================================
echo.

:: Change to the script's directory
cd /d "%~dp0"

echo [1/3] Processing any new PDF invoices...
python invoice_processor.py
echo.

echo [2/3] Starting API server...
start "Invoice API Server" cmd /k "python api_server.py"

:: Wait a moment for the server to start
timeout /t 2 /nobreak > nul

echo [3/3] Opening web application...
start "" "http://localhost:8000"

echo.
echo ============================================
echo    System Started Successfully!
echo ============================================
echo.
echo - API Server is running in a separate window
echo - Web app should open in your browser
echo - To stop: close the API Server window
echo.
echo You can close this window now.
pause
