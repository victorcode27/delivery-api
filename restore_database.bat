@echo off
REM PostgreSQL Database Restore Script
REM Restores the delivery_db database from a backup file

title PostgreSQL Database Restore

echo ============================================
echo    PostgreSQL Database Restore Tool
echo ============================================
echo.

REM Set variables
set DB_NAME=delivery_db
set DB_USER=postgres
set DB_HOST=localhost
set DB_PORT=5432
set BACKUP_DIR=%~dp0backups
set PGPASSWORD=1234

REM List available backups
echo Available backups:
echo.
dir /b /o-d "%BACKUP_DIR%\*.sql" 2>nul
echo.

REM Prompt for backup file
set /p BACKUP_FILE="Enter backup filename (or full path): "

REM Check if file exists in backups directory
if not exist "%BACKUP_FILE%" (
    if exist "%BACKUP_DIR%\%BACKUP_FILE%" (
        set BACKUP_FILE=%BACKUP_DIR%\%BACKUP_FILE%
    ) else (
        echo.
        echo ERROR: Backup file not found!
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo    WARNING: This will REPLACE all data!
echo ============================================
echo.
echo Database: %DB_NAME%
echo Backup file: %BACKUP_FILE%
echo.
set /p CONFIRM="Type YES to confirm restore: "

if /i not "%CONFIRM%"=="YES" (
    echo.
    echo Restore cancelled.
    pause
    exit /b 0
)

echo.
echo Restoring database...
echo.

REM Drop and recreate database (requires superuser)
echo Step 1: Dropping existing database...
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d postgres -c "DROP DATABASE IF EXISTS %DB_NAME%;"

echo Step 2: Creating fresh database...
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d postgres -c "CREATE DATABASE %DB_NAME%;"

echo Step 3: Restoring data...
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f "%BACKUP_FILE%"

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo    Restore completed successfully!
    echo ============================================
    echo.
) else (
    echo.
    echo ============================================
    echo    ERROR: Restore failed!
    echo ============================================
    echo.
)

REM Clean up
set PGPASSWORD=

echo.
pause
