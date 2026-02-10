@echo off
:: Firewall Setup for Delivery Route System - LAN Access
:: Run this as Administrator

title Firewall Setup - Delivery Route API

echo ============================================
echo    Firewall Setup for LAN Access
echo ============================================
echo.
echo This script will add a Windows Firewall rule to allow
echo other PCs on your network to access the API server.
echo.
echo Rule Details:
echo - Name: Delivery Route API - Port 8000
echo - Port: TCP 8000
echo - Direction: Inbound
echo - Profile: Private network only
echo.

:: Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Creating firewall rule...
echo.

:: Create the firewall rule
netsh advfirewall firewall add rule ^
    name="Delivery Route API - Port 8000" ^
    dir=in ^
    action=allow ^
    protocol=TCP ^
    localport=8000 ^
    profile=private

if %errorLevel% equ 0 (
    echo.
    echo ============================================
    echo    Firewall Rule Created Successfully!
    echo ============================================
    echo.
    echo Other PCs on your network can now access the server.
    echo.
    echo Next steps:
    echo 1. Start the server using START.bat
    echo 2. Note your IP address from the startup message
    echo 3. On other PCs, open: http://YOUR_IP:8000
    echo.
) else (
    echo.
    echo ERROR: Failed to create firewall rule!
    echo.
    echo Possible causes:
    echo - Not running as Administrator
    echo - Rule already exists
    echo.
    echo To remove existing rule and try again:
    echo netsh advfirewall firewall delete rule name="Delivery Route API - Port 8000"
    echo.
)

pause
