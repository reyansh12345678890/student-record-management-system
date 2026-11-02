# CSET333 – Problem Solving Using C — Project Report

## Project Title
**Student Record Management & Analytics System**

## 1. Problem Statement
Colleges often track student marks in registers or spreadsheets, which makes
searching, sorting, and computing class statistics slow and error-prone.
This project builds a menu-driven C program that stores student records
(roll number, name, marks in 5 subjects, auto-calculated percentage) in
dynamic memory, supports add / display / search / update / delete / sort /
statistics operations, and persists records to a file so they survive
between runs.

## 2. Project Objectives
- Store student records using structures and dynamic memory (no fixed limits).
- Provide CRUD operations through a simple menu.
- Search records by roll number using a searching algorithm.
- Sort records by roll number or percentage using a hand-written sorting
  algorithm driven by a **function pointer** (the advanced C concept).
- Compute class analytics: count, average, highest, lowest, pass/fail counts.
- Save/load records with file handling.
- Validate all input and handle every failure gracefully (bad input,
  duplicates, empty list, malloc failure, missing file).

## 3. Features
1. **Add Student** – roll no., name, 5 subject marks; percentage auto-calculated;
   duplicate roll numbers rejected; marks validated to 0–100.
2. **Display All Students** – neat table with PASS/FAIL result.
3. **Search Student** – linear search by roll number.
4. **Update Student** – change name and marks (percentage recalculated).
5. **Delete Student** – removes record, shifts the array left.
6. **Sort Students** – by roll number or by percentage (bubble sort +
   function pointer comparator).
7. **Calculate Statistics** – count, average, highest, lowest, passed, failed.
8. **Save Records** – binary file `students.dat`.
9. **Load Records** – automatic at program start.
10. **Exit** – auto-saves, frees memory.

## 4. C Concepts Demonstrated (mapped to the guidelines)
| # | Required concept | Where it appears |
|---|---|---|
| 1 | Functions | Every feature is a function (`addStudent`, `sortStudents`, …) |
| 2 | Arrays | `float marks[5]` inside the struct |
| 3 | Strings | `char name[50]`; `fgets`, `strlen`, `strcspn` |
| 4 | Loops & control | `for`/`while`/`do-while`, `if-else`, `switch` (menu) |
| 5 | Pointers | `Student *`, `FILE *`, pointer-to-structure (`s->rollNo`) |
| 6 | Structures / typedef | `typedef struct { … } Student;` |
| 7 | Searching | `findStudentByRoll` – linear search |
| 8 | Sorting / algorithms | `sortStudents` – hand-written bubble sort |
| 9 | Dynamic memory / typecasting | `malloc` / `realloc` / `free`, `(Student *)` casts |
| 10 | Advanced concept | **Function pointers**: `int (*compare)(const Student *, const Student *)` |

## 5. Data Structure Design
```c
typedef struct {
    int   rollNo;          // unique key
    char  name[50];        // string (character array)
    float marks[5];        // array of 5 subject marks
    float percentage;      // derived field = average of marks
} Student;
```
- The "database" is a **dynamic array**: `Student *students` + `count` + `capacity`.
- Starts at capacity 2; doubles via `realloc` whenever full → no fixed limit.
- `percentage` is stored (not recomputed on every display) but **recalculated
  on add and update** so it can never go stale.

## 6. Algorithm Explanation
- **Linear search** (`findStudentByRoll`): scan index 0 → count-1, compare
  `rollNo`; return index on match, else -1. Time: O(n). Simple and correct
  for an unsorted, modest-size list.
- **Bubble sort** (`sortStudents`): repeat passes over the array; each pass
  bubbles the largest (per the comparator) element to the end by swapping
  adjacent out-of-order pairs. Time: O(n²). Written manually per guidelines.
- **Function-pointer comparator**: `sortStudents` receives
  `int (*compare)(const Student *, const Student *)`. It calls
  `compare(&students[j], &students[j+1])` and swaps when the result is > 0.
  Passing `compareByRoll` sorts by roll number; passing
  `compareByPercentageDesc` sorts by percentage — **one sort routine,
  many orderings**.
- **Dynamic growth**: when `count == capacity`, `realloc` doubles capacity.
  Amortised cost of adding is O(1).
- **Delete**: linear search for index, then shift elements `index … count-2`
  one slot left, `count--`. O(n).
- **Statistics**: single O(n) pass tracking sum, max, min, pass count.

## 7. Architecture / Flow of the Program
```
USER
  ↓
COMMAND / MENU            (printMenu + switch in main)
  ↓
INPUT PROCESSING          (readInt / readMark / readName — all validated)
  ↓
DATA LAYER + ALGORITHMS   (dynamic array; linear search; bubble sort
                           via function pointer; statistics pass)
  ↓
STRUCTURES + FUNCTIONS    (typedef struct Student; one function per feature)
  ↓
OUTPUT LAYER              (tables, detail view, statistics, file students.dat)
```
Program flow: `main` → `malloc` initial array → `loadRecords` (auto-load) →
menu loop (`do-while` + `switch`) → on exit: `saveRecords` → `free`.

## 8. Complete C Source Code
See `student_record_management.c` (pure C, compiles with
`gcc student_record_management.c -o student_record_management`).

## 9. Test Cases
| # | Test | Input | Expected | Result |
|---|---|---|---|---|
| 1 | Add valid student | roll 101, name, marks 80 85 90 75 88 | "Student added successfully", 83.60% | ✅ PASS |
| 2 | Duplicate roll | add roll 101 again | "already exists", rejected | ✅ PASS |
| 3 | Invalid marks | 150, then -5, then 70 | first two rejected, 70 accepted | ✅ PASS |
| 4 | Empty name | press Enter at name prompt | "Name cannot be empty", re-prompt | ✅ PASS |
| 5 | Non-numeric menu choice | type `abc` | "Invalid input", re-prompt | ✅ PASS |
| 6 | Out-of-range menu choice | 77 | "Invalid choice", re-prompt | ✅ PASS |
| 7 | Search existing | roll 101 | full details shown | ✅ PASS |
| 8 | Search non-existing | roll 999 | "not found" | ✅ PASS |
| 9 | Update student | roll 102, new name + marks | "updated", percentage recalculated | ✅ PASS |
| 10 | Delete student | roll 101 | "deleted", list shrinks | ✅ PASS |
| 11 | Sort by percentage | 3 students | order 100%, 80%, 30% | ✅ PASS |
| 12 | Sort by roll | — | ascending roll order | ✅ PASS |
| 13 | Statistics | 100/80/30 % | avg 70.00, high/low named, 2 pass 1 fail | ✅ PASS |
| 14 | Empty list ops | display/search/update/delete/sort/stats | friendly "No records" messages, no crash | ✅ PASS |
| 15 | File not found | delete `students.dat`, run | "No saved records… starting empty" | ✅ PASS |
| 16 | Save + reload | save, exit, restart | "Loaded N record(s)", data intact | ✅ PASS |
| 17 | Memory growth | add 3rd student (capacity 2) | "(Memory expanded to hold 4 students.)" | ✅ PASS |
| 18 | malloc failure | code review | every `malloc`/`realloc` NULL-checked with message | ✅ PASS |
| 19 | Compiler hygiene | `gcc -Wall -Wextra -std=c11` | zero warnings | ✅ PASS |
| 20 | Blank-screen fix (v1.1) | `setvbuf(stdout, NULL, _IONBF, 0)` in `main`; `.bat` converted to CRLF line endings | prompts appear immediately in all terminals/IDEs; batch file runs correctly on Windows cmd.exe | ✅ PASS |

## 10. Expected Output (sample run)
```
Loading saved records...
No saved records found. Starting with an empty list.

============================================
   STUDENT RECORD MANAGEMENT & ANALYTICS
============================================
1. Add Student
...
Enter your choice (1-9): 1
Enter roll number: 101
Enter name: Aarav Sharma
Enter marks for subject 1 (0-100): 80
...
Student added successfully.

Roll No    Name                 Percentage   Result
-----------------------------------------------------
101        Aarav Sharma         83.60        PASS
102        Diya Patel           43.00        PASS

----- Class Statistics -----
Number of students : 2
Average percentage : 63.30%
Highest percentage : 83.60% (Roll No 101, Aarav Sharma)
Lowest percentage  : 43.00% (Roll No 102, Diya Patel)
Passed             : 2
Failed             : 0
```

## 11. Future Enhancements
- Binary search option after sorting by roll number.
- Export to CSV for Excel.
- Edit individual subject marks instead of all five.
- Linked-list version for comparison of data structures.
- Password-protected teacher mode.
- Graphical report (bar chart of percentages) using a simple graphics lib.

## 12. Viva / Oral-Assessment Q&A
The key questions, each answered in plain language:

**1. Why `struct`?**
One student is not one value — it is a roll number, a name, 5 marks and a
percentage that belong together. A `struct` groups them into a single
`Student` record, so an array of `Student` works like a table: one row
per student, with every field travelling together when records are
copied, sorted or saved.

**2. Why `typedef`?**
Without it, every declaration would have to say `struct Student`. With
`typedef struct { ... } Student;` I can just write `Student` everywhere —
`Student *students`, `Student s;` — which is shorter and reads like a
built-in type. It changes nothing about how the data is stored.

**3. Why pointers?**
Three reasons in this project. (a) Functions must change the caller's
data: `updateStudent` writes new marks through a `Student *`, otherwise
it would change only a copy and the update would be lost. (b) A pointer
is just one address, while a `Student` is 80 bytes — passing the record
itself by value would copy all 80 bytes. Functions that only read, like
`displayStudent`, take `const Student *` so the compiler stops them
changing the record. (c) The dynamic array and the file are both handled
through pointers (`Student *`, `FILE *`).

**4. Why `Student **`?**
`addStudent` and `loadRecords` can replace the array itself: `realloc`
may move it to a new address, and loading discards the small initial
array for the loaded one. To update the caller's own pointer variable —
not just the records it points to — the function needs the address of
that pointer, which is a pointer to a pointer: `Student **`.

**5. How do `malloc` / `realloc` / `free` work here?**
`main` starts with `malloc` for capacity 2. When the array is full,
`addStudent` uses `realloc` to double the capacity. The result is stored
in a temporary pointer first: if `realloc` fails and returns `NULL`, the
old array is still safe and no record is lost; only on success is the
original pointer updated. Every `malloc`/`realloc` result is
NULL-checked. On exit, `free(students)` returns the heap memory.

**6. How does searching work?**
Linear search. `findStudentByRoll` scans from index 0 to `count - 1`,
compares each `rollNo`, returns the index on a match or `-1` if not
found. Time is O(n). It is reused by search, update, delete, and the
duplicate-roll check in `addStudent`, so there is one search routine,
not four copies.

**7. How does sorting work?**
A hand-written bubble sort in `sortStudents`: repeated passes compare
neighbouring records and swap them when they are out of order, so the
largest (per the comparator) bubbles to the end of each pass. Time is
O(n²), which is fine for a class-size list, and writing it by hand was
a course requirement — no library sort is used.

**8. How does the function pointer work?**
`sortStudents` does not know what "in order" means. It receives
`int (*compare)(const Student *, const Student *)` and swaps only when
`compare(a, b) > 0`. Passing `compareByRoll` sorts ascending by roll
number; passing `compareByPercentageDesc` sorts highest percentage
first. One sort routine, no duplicated code. Note that
`compareByPercentageDesc` does not subtract: percentage is a `float`,
and returning the difference as an `int` would truncate it (83.6 vs
83.2 would look equal), so it returns 1 / -1 / 0 with explicit `if`s.

**9. How does file handling work?**
Records persist in a binary file, `students.dat`. `saveRecords` opens
it with `fopen(..., "wb")`, writes the record count first with
`fwrite`, then all the `Student` records. `loadRecords` runs
automatically at startup: it reads the count, allocates exactly that
many records, and checks that `fread` actually returned that many —
a short read means the file is incomplete or corrupted. A missing file
is not an error; the program just starts with an empty list. Records
auto-save on exit (menu option 9).

**10. How are the CSET333 requirements met?**
All ten required concepts are in the one pure-C source file, mapped in
Section 4 above: functions (one per feature), arrays (`marks[5]`),
strings (`name[50]`, `fgets`), loops and `switch` control, pointers,
structures/`typedef`, linear searching, hand-written bubble sorting,
dynamic memory (`malloc`/`realloc`/`free`), and the advanced concept —
function pointers driving the sort. No C++, no other language, no
external libraries.
