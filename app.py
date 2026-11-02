"""=============================================================================
FILE DEFINITION: app.py
=============================================================================
PROJECT TITLE : Student Record Management & Analytics System
COURSE        : CSET333 - Problem Solving Using C
SUBSYSTEM     : Localhost Web Deployment & REST API Server
FRAMEWORK     : Python 3 / Flask

PURPOSE & DESCRIPTION:
  This file serves the localhost web deployment on http://localhost:5000.
  It provides:
    1. A responsive, modern Web UI dashboard for student record operations.
    2. A comprehensive REST API for full CRUD functionality and analytics.
    3. Direct binary interoperability with "students.dat" using Python's struct
       module, matching the exact memory struct layout of student_record_management.c.
    4. An integrated C execution runner (/api/c-run) that invokes the compiled C
       binary (student_record_management.exe) and relays terminal output to the web.

MEMORY / BINARY COMPATIBILITY:
  Matches the C struct Student layout (80 bytes total):
    - int rollNo      : 4 bytes (little-endian '<i')
    - char name[50]   : 50 bytes ('50s')
    - padding         : 2 bytes ('2x' for 4-byte float boundary alignment)
    - float marks[5]  : 20 bytes ('5ff')
    - float percentage: 4 bytes ('f')
  Struct Format: "<i50s2x5ff"
============================================================================="""

import os
import struct
import subprocess
from flask import Flask, jsonify, render_template_string, request

# Initialize Flask web application
app = Flask(__name__)

# Constants matching C project definitions
DATA_FILE = "students.dat"
C_BINARY = "student_record_management.exe"

# Binary struct layout matching student_record_management.c
STUDENT_STRUCT_FMT = "<i50s2x5ff"
STUDENT_STRUCT_SIZE = struct.calcsize(STUDENT_STRUCT_FMT)  # Exact 80 bytes


# =============================================================================
# BINARY FILE PERSISTENCE HELPERS (Exact C Binary Interoperability)
# =============================================================================

def load_records_from_dat():
    """
    Reads student records from the binary file 'students.dat'.
    Unpacks records into Python dictionaries identical to the C array format.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "rb") as f:
            header = f.read(4)
            if len(header) < 4:
                return []
            (count,) = struct.unpack("<i", header)
            students = []
            for _ in range(count):
                record_bytes = f.read(STUDENT_STRUCT_SIZE)
                if len(record_bytes) < STUDENT_STRUCT_SIZE:
                    break
                roll, name_raw, m1, m2, m3, m4, m5, pct = struct.unpack(
                    STUDENT_STRUCT_FMT, record_bytes
                )
                # Decode null-padded C character array to clean string
                name = name_raw.decode("utf-8", errors="replace").split("\x00")[0].strip()
                marks = [round(float(m), 2) for m in (m1, m2, m3, m4, m5)]
                students.append(
                    {
                        "rollNo": int(roll),
                        "name": name,
                        "marks": marks,
                        "percentage": round(float(pct), 2),
                        "result": "PASS" if pct >= 40.0 else "FAIL",
                    }
                )
            return students
    except Exception as e:
        print(f"Error reading {DATA_FILE}: {e}")
        return []


def save_records_to_dat(students):
    """
    Serializes student dictionaries into the exact binary structure and writes to 'students.dat'.
    Enables instant two-way synchronization with the C executable.
    """
    try:
        with open(DATA_FILE, "wb") as f:
            count = len(students)
            # Write 4-byte record count header
            f.write(struct.pack("<i", count))
            for s in students:
                # Truncate and pad string to 50 bytes with null characters
                name_bytes = s["name"].encode("utf-8")[:49]
                name_bytes = name_bytes.ljust(50, b"\x00")
                m = s["marks"]
                record = struct.pack(
                    STUDENT_STRUCT_FMT,
                    int(s["rollNo"]),
                    name_bytes,
                    float(m[0]),
                    float(m[1]),
                    float(m[2]),
                    float(m[3]),
                    float(m[4]),
                    float(s["percentage"]),
                )
                f.write(record)
        return True
    except Exception as e:
        print(f"Error writing {DATA_FILE}: {e}")
        return False


def compute_statistics(students):
    """
    Computes class-wide performance metrics:
    count, class average percentage, top student, lowest student, pass/fail counts.
    """
    count = len(students)
    if count == 0:
        return {
            "count": 0,
            "average": 0.0,
            "highest": None,
            "lowest": None,
            "passed": 0,
            "failed": 0,
            "passRate": 0.0,
        }

    total_pct = sum(s["percentage"] for s in students)
    avg_pct = round(total_pct / count, 2)
    top_student = max(students, key=lambda s: s["percentage"])
    low_student = min(students, key=lambda s: s["percentage"])
    passed_count = sum(1 for s in students if s["percentage"] >= 40.0)
    failed_count = count - passed_count
    pass_rate = round((passed_count / count) * 100, 1)

    return {
        "count": count,
        "average": avg_pct,
        "highest": {
            "rollNo": top_student["rollNo"],
            "name": top_student["name"],
            "percentage": top_student["percentage"],
        },
        "lowest": {
            "rollNo": low_student["rollNo"],
            "name": low_student["name"],
            "percentage": low_student["percentage"],
        },
        "passed": passed_count,
        "failed": failed_count,
        "passRate": pass_rate,
    }


# =============================================================================
# FRONTEND HTML / CSS / JS TEMPLATE
# =============================================================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Student Record Management & Analytics System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --success: #10b981;
      --danger: #ef4444;
      --warning: #f59e0b;
      --purple: #8b5cf6;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 24px;
      line-height: 1.5;
    }

    .container { max-width: 1200px; margin: 0 auto; }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 28px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--card-border);
    }
    .badge {
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 9999px;
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .badge-c {
      background: rgba(139, 92, 246, 0.15);
      color: #c084fc;
      border-color: rgba(139, 92, 246, 0.3);
    }
    h1 { font-size: 1.65rem; font-weight: 700; margin-top: 6px; }
    .subtitle { color: var(--text-muted); font-size: 0.9rem; }

    .header-actions { display: flex; gap: 10px; align-items: center; }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--accent);
      color: white;
      border: none;
      padding: 9px 18px;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn:hover { background: var(--accent-hover); transform: translateY(-1px); }
    .btn-secondary {
      background: #334155;
      color: #e2e8f0;
    }
    .btn-secondary:hover { background: #475569; }
    .btn-danger { background: #dc2626; }
    .btn-danger:hover { background: #b91c1c; }
    .btn-outline {
      background: transparent;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
    }
    .btn-outline:hover { background: rgba(255,255,255,0.05); color: var(--text); }

    /* STATS GRID */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 18px;
      position: relative;
      overflow: hidden;
    }
    .stat-card .label {
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 600;
    }
    .stat-card .value {
      font-size: 1.85rem;
      font-weight: 700;
      margin-top: 6px;
    }
    .stat-card .subtext {
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .stat-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: var(--accent);
    }
    .stat-card.pass::before { background: var(--success); }
    .stat-card.fail::before { background: var(--danger); }
    .stat-card.purple::before { background: var(--purple); }

    /* CONTROLS BAR */
    .controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }
    .search-box {
      flex: 1;
      min-width: 260px;
      position: relative;
    }
    .search-box input {
      width: 100%;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 10px 14px 10px 38px;
      color: var(--text);
      font-size: 0.9rem;
    }
    .search-box input:focus {
      outline: none;
      border-color: var(--accent);
    }
    .search-icon {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
    }

    .sort-group {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .select-dropdown {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text);
      padding: 9px 14px;
      border-radius: 8px;
      font-size: 0.88rem;
      cursor: pointer;
    }
    .select-dropdown:focus { outline: none; border-color: var(--accent); }

    /* TABLE */
    .table-container {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
    }
    thead {
      background: rgba(15, 23, 42, 0.6);
      border-bottom: 1px solid var(--card-border);
    }
    th {
      padding: 14px 16px;
      font-weight: 600;
      color: var(--text-muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }
    td {
      padding: 14px 16px;
      border-bottom: 1px solid rgba(51, 65, 85, 0.5);
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: rgba(255, 255, 255, 0.02); }

    .roll-badge {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: #93c5fd;
    }
    .status-badge {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }
    .status-pass {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-fail {
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .marks-tags {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
    .mark-tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      background: rgba(255,255,255,0.06);
      padding: 2px 6px;
      border-radius: 4px;
      color: #cbd5e1;
    }

    .action-btns {
      display: flex;
      gap: 8px;
    }
    .icon-btn {
      background: transparent;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      transition: all 0.2s;
    }
    .icon-btn:hover {
      background: rgba(255,255,255,0.1);
      color: var(--text);
    }
    .icon-btn-delete:hover {
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      border-color: rgba(239, 68, 68, 0.4);
    }

    .empty-state {
      padding: 48px 16px;
      text-align: center;
      color: var(--text-muted);
    }

    /* MODAL */
    .modal-overlay {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal {
      background: #1e293b;
      border: 1px solid var(--card-border);
      border-radius: 14px;
      width: 100%;
      max-width: 520px;
      padding: 24px;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    .modal-title { font-size: 1.25rem; font-weight: 700; }
    .close-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 1.5rem;
      cursor: pointer;
    }
    .form-group {
      margin-bottom: 16px;
    }
    .form-group label {
      display: block;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 6px;
    }
    .form-group input {
      width: 100%;
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 10px 12px;
      color: var(--text);
      font-size: 0.9rem;
    }
    .form-group input:focus { outline: none; border-color: var(--accent); }
    .marks-inputs-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
    }
    .marks-inputs-grid input {
      text-align: center;
      font-family: 'JetBrains Mono', monospace;
    }
    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 24px;
    }

    /* TERMINAL DRAWER */
    .terminal-section {
      margin-top: 28px;
      background: #090d16;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow: hidden;
    }
    .terminal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #111827;
      padding: 10px 16px;
      border-bottom: 1px solid var(--card-border);
      font-size: 0.82rem;
      color: var(--text-muted);
    }
    .terminal-body {
      padding: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: #38bdf8;
      white-space: pre-wrap;
      max-height: 250px;
      overflow-y: auto;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span class="badge">Localhost Active</span>
          <span class="badge badge-c">CSET333 - Binary Synced</span>
        </div>
        <h1>Student Record Management & Analytics System</h1>
        <div class="subtitle">Problem Solving Using C • Local Web Deployment & C Binary Interface</div>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" onclick="runCBinary()">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 17l6-6-6-6m8 14h8"/></svg>
          Run C Program
        </button>
        <button class="btn btn-secondary" onclick="seedSampleData()">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Demo Data
        </button>
        <button class="btn" onclick="openAddModal()">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4"/></svg>
          Add Student
        </button>
      </div>
    </header>

    <!-- CLASS STATS -->
    <div class="stats-grid" id="statsGrid">
      <div class="stat-card">
        <div class="label">Total Students</div>
        <div class="value" id="statCount">0</div>
        <div class="subtext">Active records in students.dat</div>
      </div>
      <div class="stat-card purple">
        <div class="label">Class Average</div>
        <div class="value" id="statAvg">0.00%</div>
        <div class="subtext">Across all subjects</div>
      </div>
      <div class="stat-card pass">
        <div class="label">Top Performer</div>
        <div class="value" id="statTop">None</div>
        <div class="subtext" id="statTopDetail">Highest percentage</div>
      </div>
      <div class="stat-card">
        <div class="label">Lowest Performer</div>
        <div class="value" id="statLow">None</div>
        <div class="subtext" id="statLowDetail">Lowest percentage</div>
      </div>
      <div class="stat-card pass">
        <div class="label">Pass / Fail</div>
        <div class="value" id="statPassFail">0 / 0</div>
        <div class="subtext" id="statPassRate">Pass criteria: >= 40%</div>
      </div>
    </div>

    <!-- CONTROLS -->
    <div class="controls">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Search by Roll No or Student Name..." oninput="handleSearch()">
      </div>
      <div class="sort-group">
        <label style="font-size: 0.85rem; color: var(--text-muted);">Sort by:</label>
        <select class="select-dropdown" id="sortSelect" onchange="fetchStudents()">
          <option value="default">Default Order</option>
          <option value="roll">Roll No (Ascending)</option>
          <option value="percentage">Percentage (Highest First)</option>
        </select>
        <button class="btn btn-outline" onclick="fetchStudents()" title="Reload data">↻ Refresh</button>
      </div>
    </div>

    <!-- TABLE -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Roll No</th>
            <th>Student Name</th>
            <th>5 Subject Marks</th>
            <th>Percentage</th>
            <th>Result</th>
            <th style="text-align: right;">Actions</th>
          </tr>
        </thead>
        <tbody id="studentsTableBody">
          <tr><td colspan="6" class="empty-state">Loading students...</td></tr>
        </tbody>
      </table>
    </div>

    <!-- C CONSOLE DRAWER -->
    <div class="terminal-section">
      <div class="terminal-header">
        <span>📟 CSET333 C Engine Console Output (`student_record_management.exe`)</span>
        <span style="font-size: 0.75rem;">Source: student_record_management.c</span>
      </div>
      <div class="terminal-body" id="terminalOutput">Click "Run C Program" to execute the compiled C binary and verify its exact terminal output here.</div>
    </div>
  </div>

  <!-- ADD / EDIT MODAL -->
  <div class="modal-overlay" id="studentModal">
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title" id="modalTitle">Add Student Record</h3>
        <button class="close-btn" onclick="closeModal()">&times;</button>
      </div>
      <form id="studentForm" onsubmit="handleFormSubmit(event)">
        <input type="hidden" id="editMode" value="false">
        <div class="form-group">
          <label for="formRoll">Roll Number</label>
          <input type="number" id="formRoll" required min="1" placeholder="e.g. 101">
        </div>
        <div class="form-group">
          <label for="formName">Student Name</label>
          <input type="text" id="formName" required maxlength="49" placeholder="e.g. John Doe">
        </div>
        <div class="form-group">
          <label>5 Subject Marks (0 - 100)</label>
          <div class="marks-inputs-grid">
            <input type="number" id="m1" step="0.1" min="0" max="100" placeholder="Sub 1" required>
            <input type="number" id="m2" step="0.1" min="0" max="100" placeholder="Sub 2" required>
            <input type="number" id="m3" step="0.1" min="0" max="100" placeholder="Sub 3" required>
            <input type="number" id="m4" step="0.1" min="0" max="100" placeholder="Sub 4" required>
            <input type="number" id="m5" step="0.1" min="0" max="100" placeholder="Sub 5" required>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn" id="saveBtn">Save Record</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    let allStudents = [];

    // Fetch student list with optional sort query
    async function fetchStudents() {
      const sortVal = document.getElementById('sortSelect').value;
      const res = await fetch(`/api/students?sort=${sortVal}`);
      allStudents = await res.json();
      renderTable(allStudents);
      fetchStats();
    }

    // Fetch and populate statistical metrics
    async function fetchStats() {
      const res = await fetch('/api/stats');
      const stats = await res.json();
      document.getElementById('statCount').innerText = stats.count;
      document.getElementById('statAvg').innerText = stats.average.toFixed(2) + '%';
      if (stats.highest) {
        document.getElementById('statTop').innerText = stats.highest.percentage.toFixed(2) + '%';
        document.getElementById('statTopDetail').innerText = `#${stats.highest.rollNo} - ${stats.highest.name}`;
      } else {
        document.getElementById('statTop').innerText = 'None';
        document.getElementById('statTopDetail').innerText = 'Highest percentage';
      }
      if (stats.lowest) {
        document.getElementById('statLow').innerText = stats.lowest.percentage.toFixed(2) + '%';
        document.getElementById('statLowDetail').innerText = `#${stats.lowest.rollNo} - ${stats.lowest.name}`;
      } else {
        document.getElementById('statLow').innerText = 'None';
        document.getElementById('statLowDetail').innerText = 'Lowest percentage';
      }
      document.getElementById('statPassFail').innerText = `${stats.passed} / ${stats.failed}`;
      document.getElementById('statPassRate').innerText = `Pass rate: ${stats.passRate}% (cutoff >= 40%)`;
    }

    // Render HTML table rows
    function renderTable(students) {
      const tbody = document.getElementById('studentsTableBody');
      if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No student records found. Click <strong>Add Student</strong> or <strong>Demo Data</strong> above.</td></tr>`;
        return;
      }

      tbody.innerHTML = students.map(s => `
        <tr>
          <td><span class="roll-badge">${s.rollNo}</span></td>
          <td style="font-weight: 500;">${escapeHtml(s.name)}</td>
          <td>
            <div class="marks-tags">
              ${s.marks.map((m, idx) => `<span class="mark-tag">S${idx+1}: ${m}</span>`).join('')}
            </div>
          </td>
          <td style="font-weight: 600;">${s.percentage.toFixed(2)}%</td>
          <td>
            <span class="status-badge ${s.result === 'PASS' ? 'status-pass' : 'status-fail'}">${s.result}</span>
          </td>
          <td style="text-align: right;">
            <div class="action-btns" style="justify-content: flex-end;">
              <button class="icon-btn" onclick="openEditModal(${s.rollNo})">Edit</button>
              <button class="icon-btn icon-btn-delete" onclick="deleteStudentRecord(${s.rollNo})">Delete</button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    // Real-time client-side filter
    function handleSearch() {
      const q = document.getElementById('searchInput').value.trim().toLowerCase();
      if (!q) {
        renderTable(allStudents);
        return;
      }
      const filtered = allStudents.filter(s =>
        s.rollNo.toString().includes(q) || s.name.toLowerCase().includes(q)
      );
      renderTable(filtered);
    }

    // Open Add Student Modal Dialog
    function openAddModal() {
      document.getElementById('modalTitle').innerText = 'Add Student Record';
      document.getElementById('editMode').value = 'false';
      document.getElementById('formRoll').disabled = false;
      document.getElementById('formRoll').value = '';
      document.getElementById('formName').value = '';
      document.getElementById('m1').value = '';
      document.getElementById('m2').value = '';
      document.getElementById('m3').value = '';
      document.getElementById('m4').value = '';
      document.getElementById('m5').value = '';
      document.getElementById('studentModal').style.display = 'flex';
    }

    // Open Edit Student Modal Dialog
    function openEditModal(rollNo) {
      const s = allStudents.find(x => x.rollNo === rollNo);
      if (!s) return;
      document.getElementById('modalTitle').innerText = 'Edit Student Record';
      document.getElementById('editMode').value = 'true';
      document.getElementById('formRoll').disabled = true;
      document.getElementById('formRoll').value = s.rollNo;
      document.getElementById('formName').value = s.name;
      document.getElementById('m1').value = s.marks[0];
      document.getElementById('m2').value = s.marks[1];
      document.getElementById('m3').value = s.marks[2];
      document.getElementById('m4').value = s.marks[3];
      document.getElementById('m5').value = s.marks[4];
      document.getElementById('studentModal').style.display = 'flex';
    }

    // Close Modal Dialog
    function closeModal() {
      document.getElementById('studentModal').style.display = 'none';
    }

    // Handle Add / Edit Submission
    async function handleFormSubmit(e) {
      e.preventDefault();
      const isEdit = document.getElementById('editMode').value === 'true';
      const rollNo = parseInt(document.getElementById('formRoll').value);
      const name = document.getElementById('formName').value.trim();
      const marks = [
        parseFloat(document.getElementById('m1').value),
        parseFloat(document.getElementById('m2').value),
        parseFloat(document.getElementById('m3').value),
        parseFloat(document.getElementById('m4').value),
        parseFloat(document.getElementById('m5').value)
      ];

      const payload = { rollNo, name, marks };
      let res;
      if (isEdit) {
        res = await fetch(`/api/students/${rollNo}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        res = await fetch('/api/students', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      const data = await res.json();
      if (!res.ok) {
        alert(data.error || 'Failed to save record');
        return;
      }
      closeModal();
      fetchStudents();
    }

    // Delete Student Record
    async function deleteStudentRecord(rollNo) {
      if (!confirm(`Are you sure you want to delete student with Roll No ${rollNo}?`)) return;
      const res = await fetch(`/api/students/${rollNo}`, { method: 'DELETE' });
      if (res.ok) {
        fetchStudents();
      } else {
        const d = await res.json();
        alert(d.error || 'Failed to delete record');
      }
    }

    // Seed Sample Demonstration Data
    async function seedSampleData() {
      if (allStudents.length > 0 && !confirm('Load sample demonstration records? Existing records will be replaced.')) {
        return;
      }
      const res = await fetch('/api/seed', { method: 'POST' });
      if (res.ok) {
        fetchStudents();
      }
    }

    // Execute Compiled C Binary and display output
    async function runCBinary() {
      const term = document.getElementById('terminalOutput');
      term.innerText = 'Compiling and executing student_record_management.exe in background...';
      try {
        const res = await fetch('/api/c-run');
        const d = await res.json();
        term.innerText = d.output;
      } catch (err) {
        term.innerText = 'Error running C binary: ' + err;
      }
    }

    // Prevent XSS
    function escapeHtml(text) {
      const div = document.createElement('div');
      div.innerText = text;
      return div.innerHTML;
    }

    // Initialize on page load
    window.onload = fetchStudents;
  </script>
</body>
</html>
"""


# =============================================================================
# REST API ENDPOINTS & ROUTING
# =============================================================================

@app.route("/")
def index():
    """Serves the main interactive dashboard."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/students", methods=["GET"])
def get_students():
    """
    GET /api/students:
    Retrieves all student records from students.dat.
    Supports optional sort query parameters:
      - ?sort=roll       : Sort ascending by roll number
      - ?sort=percentage : Sort descending by percentage
    """
    students = load_records_from_dat()
    sort_by = request.args.get("sort", "default")
    if sort_by == "roll":
        students.sort(key=lambda s: s["rollNo"])
    elif sort_by == "percentage":
        students.sort(key=lambda s: s["percentage"], reverse=True)
    return jsonify(students)


@app.route("/api/students/<int:roll_no>", methods=["GET"])
def get_student(roll_no):
    """
    GET /api/students/<roll_no>:
    Searches for a single student by roll number using linear search.
    """
    students = load_records_from_dat()
    for s in students:
        if s["rollNo"] == roll_no:
            return jsonify(s)
    return jsonify({"error": f"Student with Roll No {roll_no} not found"}), 404


@app.route("/api/students", methods=["POST"])
def add_student():
    """
    POST /api/students:
    Adds a new student record to students.dat.
    Validates roll number uniqueness and marks in range [0, 100].
    Computes overall percentage.
    """
    data = request.json or {}
    roll_no = data.get("rollNo")
    name = data.get("name", "").strip()
    marks = data.get("marks", [])

    if roll_no is None or not name or len(marks) != 5:
        return jsonify({"error": "Roll number, name, and 5 subject marks are required"}), 400

    for m in marks:
        if m < 0 or m > 100:
            return jsonify({"error": "Marks must be between 0 and 100"}), 400

    students = load_records_from_dat()
    for s in students:
        if s["rollNo"] == roll_no:
            return jsonify({"error": f"Roll number {roll_no} already exists!"}), 400

    percentage = round(sum(marks) / 5.0, 2)
    new_student = {
        "rollNo": int(roll_no),
        "name": name,
        "marks": [round(float(m), 2) for m in marks],
        "percentage": percentage,
        "result": "PASS" if percentage >= 40.0 else "FAIL",
    }
    students.append(new_student)
    save_records_to_dat(students)
    return jsonify(new_student), 201


@app.route("/api/students/<int:roll_no>", methods=["PUT"])
def update_student(roll_no):
    """
    PUT /api/students/<roll_no>:
    Updates the name and marks of an existing student.
    Recalculates percentage and saves back to students.dat.
    """
    data = request.json or {}
    name = data.get("name", "").strip()
    marks = data.get("marks", [])

    if not name or len(marks) != 5:
        return jsonify({"error": "Name and 5 subject marks are required"}), 400

    for m in marks:
        if m < 0 or m > 100:
            return jsonify({"error": "Marks must be between 0 and 100"}), 400

    students = load_records_from_dat()
    target = None
    for s in students:
        if s["rollNo"] == roll_no:
            target = s
            break

    if not target:
        return jsonify({"error": f"Student with Roll No {roll_no} not found"}), 404

    target["name"] = name
    target["marks"] = [round(float(m), 2) for m in marks]
    target["percentage"] = round(sum(target["marks"]) / 5.0, 2)
    target["result"] = "PASS" if target["percentage"] >= 40.0 else "FAIL"

    save_records_to_dat(students)
    return jsonify(target)


@app.route("/api/students/<int:roll_no>", methods=["DELETE"])
def delete_student(roll_no):
    """
    DELETE /api/students/<roll_no>:
    Deletes the student record with the matching roll number.
    """
    students = load_records_from_dat()
    initial_len = len(students)
    students = [s for s in students if s["rollNo"] != roll_no]
    if len(students) == initial_len:
        return jsonify({"error": f"Student with Roll No {roll_no} not found"}), 404

    save_records_to_dat(students)
    return jsonify({"message": f"Student {roll_no} deleted successfully"})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    GET /api/stats:
    Returns calculated class metrics (average, highest, lowest, pass/fail counts).
    """
    students = load_records_from_dat()
    return jsonify(compute_statistics(students))


@app.route("/api/seed", methods=["POST"])
def seed_data():
    """
    POST /api/seed:
    Loads demo student records into students.dat for instant demonstration.
    """
    sample_students = [
        {
            "rollNo": 101,
            "name": "Aarav Sharma",
            "marks": [85.0, 92.0, 78.0, 88.0, 90.0],
            "percentage": 86.6,
            "result": "PASS",
        },
        {
            "rollNo": 102,
            "name": "Diya Patel",
            "marks": [72.0, 68.0, 75.0, 80.0, 70.0],
            "percentage": 73.0,
            "result": "PASS",
        },
        {
            "rollNo": 103,
            "name": "Rohan Verma",
            "marks": [35.0, 42.0, 38.0, 45.0, 32.0],
            "percentage": 38.4,
            "result": "FAIL",
        },
        {
            "rollNo": 104,
            "name": "Sneha Reddy",
            "marks": [95.0, 98.0, 92.0, 96.0, 94.0],
            "percentage": 95.0,
            "result": "PASS",
        },
        {
            "rollNo": 105,
            "name": "Vikram Singh",
            "marks": [60.0, 58.0, 65.0, 62.0, 59.0],
            "percentage": 60.8,
            "result": "PASS",
        },
    ]
    save_records_to_dat(sample_students)
    return jsonify({"message": "Sample data loaded successfully", "count": len(sample_students)})


@app.route("/api/c-run", methods=["GET"])
def run_c_program():
    """
    GET /api/c-run:
    Compiles (if needed) and executes the C program binary (student_record_management.exe)
    with a test sequence:
      - 2 (Display All)
      - 7 (Calculate Statistics)
      - 9 (Exit)
    Captures stdout/stderr from the C engine and returns it to the web terminal.
    """
    if not os.path.exists(C_BINARY):
        try:
            subprocess.run(
                ["gcc", "student_record_management.c", "-o", C_BINARY],
                check=True,
                capture_output=True,
            )
        except Exception as e:
            return jsonify({"output": f"GCC compilation error: {e}"})

    try:
        proc = subprocess.run(
            [f"./{C_BINARY}"],
            input="2\n7\n9\n",
            capture_output=True,
            text=True,
            timeout=5,
        )
        return jsonify({"output": proc.stdout or proc.stderr})
    except Exception as e:
        return jsonify({"output": f"Execution error: {e}"})


# =============================================================================
# SERVER ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    # Seed initial demo data if students.dat does not exist yet
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        seed_data()
    print("Starting Student Record Management System on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)
