#!/usr/bin/env bash
# =============================================================================
# FILE DEFINITION: run_localhost.sh
# =============================================================================
# PROJECT TITLE : Student Record Management & Analytics System
# COURSE        : CSET333 - Problem Solving Using C
# PLATFORM      : Linux / macOS / Unix (Bash Shell Script)
#
# PURPOSE & DESCRIPTION:
#   This shell script provides automated one-click localhost deployment for
#   Unix-like environments. It compiles the C source code with gcc, verifies
#   Python 3 and Flask dependencies, opens http://localhost:5000 in the system's
#   default browser, and runs the backend web application (app.py).
#
# USAGE:
#   chmod +x run_localhost.sh
#   ./run_localhost.sh
# =============================================================================

echo "============================================================"
echo "  Starting Localhost Deployment (CSET333 Project)"
echo "============================================================"
echo ""

# -----------------------------------------------------------------------------
# Step 1: Compile C source code with GCC
# -----------------------------------------------------------------------------
echo "[1/3] Compiling C source..."
gcc student_record_management.c -o student_record_management
if [ $? -eq 0 ]; then
    echo "      [OK] student_record_management compiled successfully."
fi

# -----------------------------------------------------------------------------
# Step 2: Ensure Python 3 and Flask are installed
# -----------------------------------------------------------------------------
echo "[2/3] Checking Python environment..."
python3 -c "import flask" 2>/dev/null || python3 -m pip install flask
echo "      [OK] Python & Flask ready."

# -----------------------------------------------------------------------------
# Step 3: Open default web browser and start Flask server
# -----------------------------------------------------------------------------
echo "[3/3] Launching web app on http://localhost:5000 ..."
if which xdg-open > /dev/null; then
    xdg-open "http://localhost:5000" &
elif which open > /dev/null; then
    open "http://localhost:5000" &
fi

echo ""
echo "============================================================"
echo "  Application running at http://localhost:5000"
echo "  Press Ctrl+C to stop the server."
echo "============================================================"
echo ""

python3 app.py
