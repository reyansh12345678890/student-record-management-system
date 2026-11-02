#!/bin/bash
# =============================================================================
# FILE DEFINITION: compile_and_run.sh
# =============================================================================
# PROJECT TITLE : Student Record Management & Analytics System
# COURSE        : CSET333 - Problem Solving Using C
# PLATFORM      : Linux / macOS / Unix (Bash Shell Script)
#
# PURPOSE & DESCRIPTION:
#   This shell script automates compilation and execution of the terminal-based
#   C program on Unix-like operating systems. It compiles
#   student_record_management.c into an executable binary using GCC and launches it.
#
# USAGE:
#   chmod +x compile_and_run.sh
#   ./compile_and_run.sh
# =============================================================================

# Step 1: Compile the C source code with GCC
echo "Compiling student_record_management.c ..."
gcc student_record_management.c -o student_record_management

# Step 2: Check compilation exit status
if [ $? -ne 0 ]; then
    echo "[ERROR] Compilation failed. Make sure GCC is installed."
    exit 1
fi

# Step 3: Run the compiled executable
echo "[OK] Compiled successfully. Launching program..."
./student_record_management
