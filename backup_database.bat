@echo off
REM PostgreSQL Database Backup Script
REM Creates a backup of the delivery_db database using pg_dump

title PostgreSQL Database Backup

echo ============================================
echo    PostgreSQL Database Backup Tool
echo ============================================
echo.

REM Set variables
set DB_NAME=delivery_db
set DB_USER=postgres
set DB_HOST=localhost
set DB_PORT=5432
set BACKUP_DIR=%~dp0backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=%BACKUP_DIR%\delivery_db_backup_%TIMESTAMP%.sql

REM Create backups directory if it doesn't exist
if not exist "%BACKUP_DIR%" (
    echo Creating backups directory...
    mkdir "%BACKUP_DIR%"
)

echo Backup location: %BACKUP_FILE%
echo.

REM Set password (pg_dump will use this environment variable)
set PGPASSWORD=1234

echo Starting backup...
echo.

REM Run pg_dump
"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -F p -f "%BACKUP_FILE%"

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo    Backup completed successfully!
    echo ============================================
    echo.
    echo Backup file: %BACKUP_FILE%
    echo.
    
    REM Get file size
    for %%A in ("%BACKUP_FILE%") do set FILESIZE=%%~zA
    echo File size: %FILESIZE% bytes
    echo.
    
    REM Count backup files
    for /f %%A in ('dir /b "%BACKUP_DIR%\*.sql" 2^>nul ^| find /c ".sql"') do set BACKUP_COUNT=%%A
    echo Total backups: %BACKUP_COUNT%
    echo.
) else (
    echo.
    echo ============================================
    echo    ERROR: Backup failed!
    echo ============================================
    echo.
    echo Please check:
    echo - PostgreSQL service is running
    echo - Connection credentials are correct
    echo - pg_dump.exe path is correct
    echo.
)

REM Clean up sensitive environment variable
set PGPASSWORD=

echo Press any key to exit...
pause > nul
