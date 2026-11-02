@echo off
REM =============================================================================
REM  FILE DEFINITION: run_localhost.bat
REM =============================================================================
REM  PROJECT TITLE : Student Record Management & Analytics System
REM  COURSE        : CSET333 - Problem Solving Using C
REM  PLATFORM      : Microsoft Windows (Command Prompt / Batch Script)
REM
REM  PURPOSE & DESCRIPTION:
REM    This batch script provides a one-click automated deployment for the
REM    localhost web application. It performs pre-flight checks, compiles the C
REM    code with MinGW GCC if available, installs Python requirements (Flask) if
REM    needed, opens the browser to http://localhost:5000, and starts app.py.
REM
REM  USAGE:
REM    Double-click run_localhost.bat in Windows Explorer, or execute:
REM    .\run_localhost.bat from the terminal.
REM =============================================================================

echo ============================================================
echo   Starting Localhost Deployment (CSET333 Project)
echo ============================================================
echo.

REM -----------------------------------------------------------------------------
REM Step 1: Check for MinGW GCC compiler and compile C source code
REM -----------------------------------------------------------------------------
echo [1/3] Checking C binary compilation...
where gcc >nul 2>nul
if %errorlevel% equ 0 (
    gcc student_record_management.c -o student_record_management.exe
    if %errorlevel% equ 0 (
        echo       [OK] student_record_management.exe compiled successfully.
    ) else (
        echo       [WARNING] GCC compilation failed. Continuing with existing binary if present.
    )
) else (
    echo       [NOTE] GCC compiler not detected in PATH, skipping C compilation.
)

REM -----------------------------------------------------------------------------
REM Step 2: Check Python environment and ensure Flask is installed
REM -----------------------------------------------------------------------------
echo [2/3] Checking Python environment...
python -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo       Flask module not found. Installing Flask via pip...
    python -m pip install flask
)
echo       [OK] Python & Flask ready.

REM -----------------------------------------------------------------------------
REM Step 3: Launch default web browser and start Flask server
REM -----------------------------------------------------------------------------
echo [3/3] Launching web app on http://localhost:5000 ...
start "" "http://localhost:5000"

echo.
echo ============================================================
echo   Application running at http://localhost:5000
echo   Press Ctrl+C in this console window to stop the server.
echo ============================================================
echo.

python app.py
pause
