STUDENT RECORD MANAGEMENT & ANALYTICS SYSTEM
CSET333 - Problem Solving Using C
============================================================

HOW TO DEPLOY / RUN

Option 1 - Localhost Web Deployment (Recommended):
  1. Double-click "run_localhost.bat" (or run: python app.py)
  2. Open your browser at http://localhost:5000
  Features full modern Web Dashboard, live analytics, search & sort,
  and dual-mode synchronization with the C binary (students.dat).

Option 2 - Windows Console (one double-click):
  1. Install MinGW GCC and add it to PATH (https://www.mingw-w64.org)
  2. Double-click "compile_and_run.bat"
  It compiles the project and launches the C console interface automatically.

Option 3 - Windows Console (manual):
  gcc student_record_management.c -o student_record_management.exe
  student_record_management.exe

Option 4 - Linux / macOS:
  chmod +x compile_and_run.sh run_localhost.sh
  ./run_localhost.sh (for Web) or ./compile_and_run.sh (for Terminal)

FILES IN THIS PACKAGE
  student_record_management.c  - complete C source (C only, no C++)
  app.py                       - Localhost web application & REST API
  run_localhost.bat            - one-click localhost web deploy script (Windows)
  run_localhost.sh             - one-click localhost web deploy script (Linux/macOS)
  compile_and_run.bat          - one-click C console deploy script for Windows
  compile_and_run.sh           - one-click C console deploy script for Linux/macOS
  PROJECT_REPORT.md            - full project documentation (12 sections)
  README.txt                   - this file

NOTES
  - Student records are saved to "students.dat" in the same folder.
  - The program auto-loads saved records every time it starts.
  - Records auto-save on exit (menu option 9).
