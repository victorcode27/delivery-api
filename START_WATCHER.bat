@echo off
echo ========================================
echo Invoice File Watcher Service
echo ========================================
echo.
echo This service will automatically detect and process new PDF invoices
echo from the network folder: \\BRD-DESKTOP-ELV\storage
echo.
echo Polling interval: 30 seconds
echo.
echo Press Ctrl+C to stop the service
echo.
echo ========================================
echo.

python file_watcher.py

pause
