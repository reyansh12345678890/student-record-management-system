@echo off
REM =============================================================================
REM  FILE DEFINITION: compile_and_run.bat
REM =============================================================================
REM  PROJECT TITLE : Student Record Management & Analytics System
REM  COURSE        : CSET333 - Problem Solving Using C
REM  PLATFORM      : Microsoft Windows (MinGW GCC / Command Prompt)
REM
REM  PURPOSE & DESCRIPTION:
REM    This batch script automates the compilation and execution of the terminal-
REM    based C program on Windows. It invokes MinGW GCC to compile
REM    student_record_management.c into student_record_management.exe and launches
REM    the interactive console interface.
REM
REM  USAGE:
REM    Double-click compile_and_run.bat, or run .\compile_and_run.bat in terminal.
REM =============================================================================

REM Step 1: Compile the C source code with MinGW GCC
echo Compiling student_record_management.c ...
gcc student_record_management.c -o student_record_management.exe

REM Step 2: Check compilation exit code
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Compilation failed. Make sure MinGW GCC is installed
    echo and added to your system PATH.
    pause
    exit /b 1
)

REM Step 3: Launch the compiled executable
echo.
echo [OK] Compiled successfully. Launching student_record_management.exe ...
echo.
student_record_management.exe

REM Step 4: Pause console so output remains visible upon exit
pause
