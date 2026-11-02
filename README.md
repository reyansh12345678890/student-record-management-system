# Student Record Management & Analytics System

[![Course](https://img.shields.io/badge/Course-CSET333%20Problem%20Solving%20Using%20C-blue.svg)](file:///student_record_management.c)
[![Language](https://img.shields.io/badge/Language-Pure%20C%20(C99)-00599C.svg?logo=c)](file:///student_record_management.c)
[![Web Deployment](https://img.shields.io/badge/Web%20App-Flask%20%2F%20Localhost-success.svg?logo=python)](file:///app.py)

A complete **Student Record Management & Analytics System** developed for **CSET333 - Problem Solving Using C**.

The project features a **pure C console application** utilizing core computer science algorithms and data structures, alongside a **modern Localhost Web Deployment** that shares real-time binary data compatibility (`students.dat`) with the C binary.

---

## 📌 Key Highlights

- **Pure C Engine (`student_record_management.c`)**:
  - **Dynamic Memory Allocation**: Array starts with capacity 2 and doubles dynamically (`malloc`, `realloc`, `free`).
  - **Sorting Algorithm with Function Pointers**: Hand-written Bubble Sort algorithm driven by function pointer comparators (`compareByRoll` and `compareByPercentageDesc`).
  - **Searching Algorithm**: Linear search by roll number ($O(n)$).
  - **Binary File Persistence**: Saves and loads binary student records (`students.dat`) with header metadata.
  - **Academic Analytics**: Calculates class average, top and lowest performers, and pass/fail distributions.

- **Localhost Web Deployment (`app.py`)**:
  - Interactive web dashboard hosted on `http://localhost:5000`.
  - **100% Binary Interoperability**: Direct binary read/write to `students.dat` using Python `struct` matching the C struct layout.
  - REST API with CRUD routes.
  - Integrated C Terminal runner to execute the C binary directly from the browser.

---

## 📂 Project Structure

```text
├── student_record_management.c  # Core C source code (Functions, Structs, Sorting, File I/O)
├── app.py                       # Localhost web server (Flask) & REST API
├── compile_and_run.bat          # One-click C console runner for Windows
├── compile_and_run.sh           # One-click C console runner for Linux / macOS
├── run_localhost.bat            # One-click localhost web deployment for Windows
├── run_localhost.sh             # One-click localhost web deployment for Linux / macOS
├── PROJECT_REPORT.md            # Comprehensive 12-section academic documentation
├── README.txt                   # Quick terminal instructions
└── README.md                    # Repository documentation
```

---

## 🚀 How to Run

### Option 1: Localhost Web Deployment (Recommended)
#### Windows:
Double-click `run_localhost.bat` or run:
```cmd
run_localhost.bat
```

#### Linux / macOS:
```bash
chmod +x run_localhost.sh
./run_localhost.sh
```
Then visit **`http://localhost:5000`** in your browser.

---

### Option 2: Pure C Console Application
#### Windows:
Double-click `compile_and_run.bat` or compile manually:
```cmd
gcc student_record_management.c -o student_record_management.exe
student_record_management.exe
```

#### Linux / macOS:
```bash
chmod +x compile_and_run.sh
./compile_and_run.sh
```

---

## 📊 C Concepts Demonstrated

| # | Concept | Implementation in `student_record_management.c` |
|---|---|---|
| 1 | **Functions** | Modular design (`addStudent`, `sortStudents`, `calculateStatistics`, etc.) |
| 2 | **Arrays** | 1D float array `marks[5]` inside student struct |
| 3 | **Strings** | `char name[50]`, safe reading via `fgets`, `strlen`, `strcspn` |
| 4 | **Loops & Control** | `while`, `do-while`, `switch-case` interactive menu |
| 5 | **Pointers** | Double pointers `Student **` for dynamic array expansion, `FILE *` |
| 6 | **Structures** | `typedef struct { ... } Student;` (80 bytes) |
| 7 | **Searching** | Linear search by roll number (`findStudentByRoll`) |
| 8 | **Sorting** | Custom Bubble Sort algorithm |
| 9 | **Dynamic Memory** | `malloc()`, `realloc()`, and `free()` |
| 10 | **Advanced Concept** | **Function Pointers** callback comparators: `int (*compare)(const Student *, const Student *)` |
| 11 | **File Handling** | Binary I/O via `fwrite()` and `fread()` storing to `students.dat` |

---

## 📝 License
Academic project for CSET333 - Problem Solving Using C.
