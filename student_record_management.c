/* =============================================================================
 * FILE DEFINITION: student_record_management.c
 * =============================================================================
 * PROJECT TITLE : Student Record Management & Analytics System
 * COURSE        : CSET333 - Problem Solving Using C
 * LANGUAGE      : Pure C (C99 standard, no external libraries)
 *
 * PURPOSE & DESCRIPTION:
 *   This is the primary core application file for the project. It provides a
 *   complete, console-based Student Record Management System with integrated
 *   analytics. The program manages student data dynamically in RAM and persists
 *   records to a binary disk file ("students.dat").
 *
 * KEY C CONCEPTS IMPLEMENTED:
 *   1. User-Defined Functions : Modular architecture with single-purpose functions.
 *   2. Arrays                 : 1D array of 5 subject marks inside the structure.
 *   3. Strings & C-Strings    : Safe name handling using fgets, strlen, and strcspn.
 *   4. Control Structures     : do-while loop for the interactive menu; switch-case.
 *   5. Pointers               : Pointers to structures and double pointers (Student **).
 *   6. Structures (typedef)   : Typedef struct storing complete student attributes.
 *   7. Searching Algorithm    : Linear search by roll number (O(n) complexity).
 *   8. Sorting Algorithm      : Custom Bubble Sort algorithm (O(n^2) complexity).
 *   9. Dynamic Memory (DMA)   : malloc(), realloc(), and free() for auto-expanding array.
 *  10. Advanced Concept       : Function Pointers for custom sorting comparator callbacks.
 *  11. File Handling          : Binary I/O (fread, fwrite) for persistent data storage.
 *
 * COMPILATION & EXECUTION:
 *   Compile : gcc student_record_management.c -o student_record_management.exe
 *   Run     : ./student_record_management.exe
 * ============================================================================= */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* =============================================================================
 * CONSTANTS & CONFIGURATION
 * ============================================================================= */
#define MAX_NAME_LEN     50      /* Maximum character length for a student's name */
#define NUM_SUBJECTS      5      /* Number of academic subjects evaluated */
#define PASS_PERCENT   40.0f     /* Minimum percentage required to pass (40%) */
#define INITIAL_CAPACITY  2      /* Starting capacity for dynamic heap array */
#define DATA_FILE "students.dat" /* Binary storage file for record persistence */

/* =============================================================================
 * DATA STRUCTURE DEFINITION
 * =============================================================================
 * One Student instance encapsulates all data attributes of an individual student.
 * Memory Layout:
 *   - rollNo     : 4 bytes (int)
 *   - name       : 50 bytes (char array)
 *   - [padding]  : 2 bytes (compiler alignment to 4-byte float boundary)
 *   - marks      : 20 bytes (5 x 4-byte floats)
 *   - percentage : 4 bytes (float)
 *   Total size   : 80 bytes (standard 32/64-bit MinGW GCC)
 * ============================================================================= */
typedef struct {
    int   rollNo;                  /* Unique student identification number */
    char  name[MAX_NAME_LEN];      /* Student full name (null-terminated string) */
    float marks[NUM_SUBJECTS];     /* Marks obtained across 5 subjects (0 - 100) */
    float percentage;              /* Computed overall percentage */
} Student;

/* =============================================================================
 * FUNCTION PROTOTYPES
 * ============================================================================= */
/* Input validation and helper routines */
void  clearInputBuffer(void);
int   readInt(const char *prompt);
float readMark(int subjectNo);
void  readName(char *name, int size);
float calculatePercentage(float marks[]);

/* Search routines */
int   findStudentByRoll(Student *students, int count, int rollNo);

/* CRUD (Create, Read, Update, Delete) operations */
int   addStudent(Student **students, int *count, int *capacity);
void  displayStudent(const Student *s);
void  displayAllStudents(Student *students, int count);
void  searchStudent(Student *students, int count);
void  updateStudent(Student *students, int count);
int   deleteStudent(Student **students, int *count);

/* Sorting routines (driven by function pointers) */
int   compareByRoll(const Student *a, const Student *b);
int   compareByPercentageDesc(const Student *a, const Student *b);
void  sortStudents(Student *students, int count,
                  int (*compare)(const Student *, const Student *));
void  sortMenu(Student *students, int count);

/* Analytics and Reporting */
void  calculateStatistics(Student *students, int count);

/* File handling / Persistence */
int   saveRecords(Student *students, int count);
int   loadRecords(Student **students, int *count, int *capacity);

/* User interface */
void  printMenu(void);

/* =============================================================================
 * MAIN FUNCTION: Program Entry Point & Event Loop
 * ============================================================================= */
int main(void) {
    /* Disable stdout buffering so prompts show instantly in IDEs and pipes */
    setvbuf(stdout, NULL, _IONBF, 0);

    /* Allocate initial heap memory for dynamic student array */
    Student *students = (Student *)malloc(INITIAL_CAPACITY * sizeof(Student));
    if (students == NULL) {
        printf("Fatal error: memory allocation failed.\n");
        return 1;
    }
    int count    = 0;                 /* Current number of active student records */
    int capacity = INITIAL_CAPACITY; /* Total capacity before realloc is required */

    /* Load saved student records from students.dat if available */
    printf("Loading saved records...\n");
    loadRecords(&students, &count, &capacity);

    int choice;
    /* Main interactive menu loop */
    do {
        printMenu();
        choice = readInt("Enter your choice (1-9): ");

        switch (choice) {
            case 1: addStudent(&students, &count, &capacity); break;
            case 2: displayAllStudents(students, count);      break;
            case 3: searchStudent(students, count);           break;
            case 4: updateStudent(students, count);           break;
            case 5: deleteStudent(&students, &count);         break;
            case 6: sortMenu(students, count);                break;
            case 7: calculateStatistics(students, count);    break;
            case 8: saveRecords(students, count);            break;
            case 9: printf("Saving records and exiting...\n");
                    saveRecords(students, count);
                    break;
            default:
                    printf("Invalid choice. Please enter a number 1-9.\n");
        }
    } while (choice != 9);

    /* Clean up dynamically allocated memory before program termination */
    free(students);
    printf("Memory freed. Goodbye!\n");
    return 0;
}

/* =============================================================================
 * INPUT VALIDATION HELPERS
 * ============================================================================= */

/*
 * clearInputBuffer:
 * Flushes leftover characters from stdin (such as newline characters after scanf)
 * to avoid unintended skips in subsequent input prompts.
 */
void clearInputBuffer(void) {
    int c;
    while ((c = getchar()) != '\n' && c != EOF) {
        /* Discard remaining characters */
    }
}

/*
 * readInt:
 * Prompts the user and safely reads an integer, continuously prompting if
 * invalid or non-numeric input is detected.
 */
int readInt(const char *prompt) {
    int value;
    while (1) {
        printf("%s", prompt);
        if (scanf("%d", &value) == 1) {
            clearInputBuffer();
            return value;
        }
        printf("Invalid input. Please enter a whole number.\n");
        clearInputBuffer();
    }
}

/*
 * readMark:
 * Prompts the user for a single subject mark and validates that it falls within
 * the acceptable academic range of 0.0 to 100.0.
 */
float readMark(int subjectNo) {
    float value;
    while (1) {
        printf("Enter marks for subject %d (0-100): ", subjectNo);
        if (scanf("%f", &value) == 1 && value >= 0.0f && value <= 100.0f) {
            clearInputBuffer();
            return value;
        }
        printf("Invalid marks. Enter a value between 0 and 100.\n");
        clearInputBuffer();
    }
}

/*
 * readName:
 * Reads a student's full name (including whitespace) using fgets, removes the
 * trailing newline, and rejects empty strings.
 */
void readName(char *name, int size) {
    while (1) {
        printf("Enter name: ");
        if (fgets(name, size, stdin) != NULL) {
            name[strcspn(name, "\n")] = '\0';  /* Strip newline character */
            if (strlen(name) > 0) {
                return;
            }
        }
        printf("Name cannot be empty. Try again.\n");
    }
}

/*
 * calculatePercentage:
 * Computes the arithmetic mean percentage across all NUM_SUBJECTS (5 subjects).
 */
float calculatePercentage(float marks[]) {
    float sum = 0.0f;
    for (int i = 0; i < NUM_SUBJECTS; i++) {
        sum += marks[i];
    }
    return sum / NUM_SUBJECTS;
}

/* =============================================================================
 * SEARCHING ALGORITHM
 * =============================================================================
 * findStudentByRoll:
 * Performs an iterative Linear Search through the dynamic array to find a student
 * by their unique roll number.
 * Returns: Array index if found, or -1 if not found.
 * Complexity: O(n) time, O(1) space.
 * ============================================================================= */
int findStudentByRoll(Student *students, int count, int rollNo) {
    for (int i = 0; i < count; i++) {
        if (students[i].rollNo == rollNo) {
            return i; /* Match found at index i */
        }
    }
    return -1;       /* Not found */
}

/* =============================================================================
 * CRUD OPERATIONS (Create, Read, Update, Delete)
 * ============================================================================= */

/*
 * addStudent:
 * Adds a new student record to the dynamic array.
 * Automatically doubles memory capacity via realloc() when capacity is exceeded.
 * Validates roll number uniqueness and marks boundaries.
 */
int addStudent(Student **students, int *count, int *capacity) {
    /* If array is full, dynamically double capacity */
    if (*count == *capacity) {
        int newCapacity = (*capacity) * 2;
        Student *temp = (Student *)realloc(*students,
                                           newCapacity * sizeof(Student));
        if (temp == NULL) {
            printf("Error: memory allocation failed. Student not added.\n");
            return 0;
        }
        *students = temp;
        *capacity = newCapacity;
        printf("(Memory expanded to hold %d students.)\n", *capacity);
    }

    Student s;   /* Local student record buffer */

    s.rollNo = readInt("Enter roll number: ");
    if (s.rollNo <= 0) {
        printf("Roll number must be a positive number.\n");
        return 0;
    }
    /* Duplicate check */
    if (findStudentByRoll(*students, *count, s.rollNo) != -1) {
        printf("Error: roll number %d already exists.\n", s.rollNo);
        return 0;
    }

    readName(s.name, MAX_NAME_LEN);

    for (int i = 0; i < NUM_SUBJECTS; i++) {
        s.marks[i] = readMark(i + 1);
    }
    s.percentage = calculatePercentage(s.marks);

    /* Copy record into the dynamic array */
    (*students)[*count] = s;
    (*count)++;

    printf("Student added successfully.\n");
    return 1;
}

/*
 * displayStudent:
 * Prints detailed information for a single student including marks breakdown.
 */
void displayStudent(const Student *s) {
    printf("\n----- Student Details -----\n");
    printf("Roll Number : %d\n", s->rollNo);
    printf("Name        : %s\n", s->name);
    printf("Marks       : ");
    for (int i = 0; i < NUM_SUBJECTS; i++) {
        printf("%.1f ", s->marks[i]);
    }
    printf("\nPercentage  : %.2f%%\n", s->percentage);
    printf("Result      : %s\n",
           s->percentage >= PASS_PERCENT ? "PASS" : "FAIL");
}

/*
 * displayAllStudents:
 * Formats and prints a tabular summary of all active student records.
 */
void displayAllStudents(Student *students, int count) {
    if (count == 0) {
        printf("No student records to display.\n");
        return;
    }
    printf("\n%-10s %-20s %-12s %-8s\n",
           "Roll No", "Name", "Percentage", "Result");
    printf("-----------------------------------------------------\n");
    for (int i = 0; i < count; i++) {
        printf("%-10d %-20s %-12.2f %-8s\n",
               students[i].rollNo,
               students[i].name,
               students[i].percentage,
               students[i].percentage >= PASS_PERCENT ? "PASS" : "FAIL");
    }
}

/*
 * searchStudent:
 * Interactive wrapper to search and display a student by roll number.
 */
void searchStudent(Student *students, int count) {
    if (count == 0) {
        printf("No student records to search.\n");
        return;
    }
    int rollNo = readInt("Enter roll number to search: ");
    int index = findStudentByRoll(students, count, rollNo);
    if (index == -1) {
        printf("Student with roll number %d not found.\n", rollNo);
    } else {
        displayStudent(&students[index]);
    }
}

/*
 * updateStudent:
 * Allows editing name and 5 subject marks for an existing student record.
 * Recalculates overall percentage upon update.
 */
void updateStudent(Student *students, int count) {
    if (count == 0) {
        printf("No student records to update.\n");
        return;
    }
    int rollNo = readInt("Enter roll number to update: ");
    int index = findStudentByRoll(students, count, rollNo);
    if (index == -1) {
        printf("Student with roll number %d not found.\n", rollNo);
        return;
    }

    printf("Updating student (roll number cannot be changed).\n");
    readName(students[index].name, MAX_NAME_LEN);
    for (int i = 0; i < NUM_SUBJECTS; i++) {
        students[index].marks[i] = readMark(i + 1);
    }
    /* Recalculate percentage after marks modification */
    students[index].percentage = calculatePercentage(students[index].marks);

    printf("Student updated successfully.\n");
}

/*
 * deleteStudent:
 * Removes a student record by shifting subsequent array elements left by one position.
 */
int deleteStudent(Student **students, int *count) {
    if (*count == 0) {
        printf("No student records to delete.\n");
        return 0;
    }
    int rollNo = readInt("Enter roll number to delete: ");
    int index = findStudentByRoll(*students, *count, rollNo);
    if (index == -1) {
        printf("Student with roll number %d not found.\n", rollNo);
        return 0;
    }

    /* Shift all elements to the right of index one slot to the left */
    for (int i = index; i < *count - 1; i++) {
        (*students)[i] = (*students)[i + 1];
    }
    (*count)--;
    printf("Student with roll number %d deleted.\n", rollNo);
    return 1;
}

/* =============================================================================
 * SORTING ALGORITHMS & FUNCTION POINTERS
 * =============================================================================
 * Demonstrates the advanced C concept: Passing function pointers as comparators
 * to enable multiple sorting orders through a single reusable sort function.
 * ============================================================================= */

/* Comparator callback: Ascending order by Roll Number */
int compareByRoll(const Student *a, const Student *b) {
    return a->rollNo - b->rollNo;
}

/* Comparator callback: Descending order by Percentage (highest percentage first) */
int compareByPercentageDesc(const Student *a, const Student *b) {
    if (a->percentage < b->percentage) return  1;
    if (a->percentage > b->percentage) return -1;
    return 0;
}

/*
 * sortStudents:
 * Custom implementation of Bubble Sort driven by a function pointer comparator.
 * Parameters:
 *   - students: pointer to the dynamic Student array
 *   - count   : number of active elements
 *   - compare : function pointer taking two const Student pointers and returning int
 */
void sortStudents(Student *students, int count,
                  int (*compare)(const Student *, const Student *)) {
    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            if (compare(&students[j], &students[j + 1]) > 0) {
                Student temp   = students[j];
                students[j]    = students[j + 1];
                students[j+1]  = temp;
            }
        }
    }
}

/*
 * sortMenu:
 * Sub-menu providing options to sort records by Roll Number or Percentage.
 */
void sortMenu(Student *students, int count) {
    if (count == 0) {
        printf("No student records to sort.\n");
        return;
    }
    printf("\n----- Sort Students -----\n");
    printf("1. Sort by Roll Number\n");
    printf("2. Sort by Percentage (highest first)\n");
    printf("3. Back\n");

    int choice = readInt("Enter your choice: ");
    switch (choice) {
        case 1:
            sortStudents(students, count, compareByRoll);
            printf("Students sorted by roll number.\n");
            break;
        case 2:
            sortStudents(students, count, compareByPercentageDesc);
            printf("Students sorted by percentage (highest first).\n");
            break;
        case 3:
            break;
        default:
            printf("Invalid sort choice.\n");
    }
}

/* =============================================================================
 * ANALYTICS & CLASS STATISTICS
 * =============================================================================
 * calculateStatistics:
 * Computes overall academic metrics across the enrolled batch:
 *   - Total student count
 *   - Class average percentage
 *   - Highest performer (Roll, Name, %)
 *   - Lowest performer (Roll, Name, %)
 *   - Number of students passed (>= 40%) and failed (< 40%)
 * ============================================================================= */
void calculateStatistics(Student *students, int count) {
    if (count == 0) {
        printf("No student records. Statistics unavailable.\n");
        return;
    }

    float sum = 0.0f;
    int topIndex = 0, lowIndex = 0, passed = 0;

    for (int i = 0; i < count; i++) {
        float p = students[i].percentage;
        sum += p;
        if (p > students[topIndex].percentage) topIndex = i;
        if (p < students[lowIndex].percentage) lowIndex = i;
        if (p >= PASS_PERCENT) passed++;
    }

    printf("\n----- Class Statistics -----\n");
    printf("Number of students : %d\n", count);
    printf("Average percentage : %.2f%%\n", sum / count);
    printf("Highest percentage : %.2f%% (Roll No %d, %s)\n",
           students[topIndex].percentage,
           students[topIndex].rollNo, students[topIndex].name);
    printf("Lowest percentage  : %.2f%% (Roll No %d, %s)\n",
           students[lowIndex].percentage,
           students[lowIndex].rollNo, students[lowIndex].name);
    printf("Passed             : %d\n", passed);
    printf("Failed             : %d\n", count - passed);
}

/* =============================================================================
 * FILE HANDLING & DATA PERSISTENCE
 * =============================================================================
 * Records are saved to disk in a compact binary format:
 *   [Header: 4-byte integer representing count]
 *   [Body: count * 80-byte Student structs]
 * ============================================================================= */

/*
 * saveRecords:
 * Writes the student count followed by the array of structs into students.dat.
 */
int saveRecords(Student *students, int count) {
    FILE *fp = fopen(DATA_FILE, "wb");   /* Write binary */
    if (fp == NULL) {
        printf("Error: could not open file for writing.\n");
        return 0;
    }
    fwrite(&count, sizeof(int), 1, fp);  /* Store record count */
    if (count > 0) {
        fwrite(students, sizeof(Student), count, fp);  /* Store binary structs */
    }
    fclose(fp);
    printf("Saved %d record(s) to file.\n", count);
    return 1;
}

/*
 * loadRecords:
 * Reads binary records from students.dat into heap memory at program startup.
 */
int loadRecords(Student **students, int *count, int *capacity) {
    FILE *fp = fopen(DATA_FILE, "rb");   /* Read binary */
    if (fp == NULL) {
        printf("No saved records found. Starting with an empty list.\n");
        return 0;   /* First-time run */
    }

    int n = 0;
    if (fread(&n, sizeof(int), 1, fp) != 1 || n < 0) {
        printf("Error: data file is corrupted.\n");
        fclose(fp);
        return 0;
    }
    if (n == 0) {
        fclose(fp);
        return 1;
    }

    Student *temp = (Student *)malloc(n * sizeof(Student));
    if (temp == NULL) {
        printf("Error: memory allocation failed while loading.\n");
        fclose(fp);
        return 0;
    }
    if (fread(temp, sizeof(Student), n, fp) != (size_t)n) {
        printf("Error: data file is incomplete.\n");
        free(temp);
        fclose(fp);
        return 0;
    }
    fclose(fp);

    /* Free original default array and assign newly loaded memory */
    free(*students);
    *students = temp;
    *count    = n;
    *capacity = n;
    printf("Loaded %d record(s) from file.\n", n);
    return 1;
}

/* =============================================================================
 * USER INTERFACE (MENU)
 * ============================================================================= */
void printMenu(void) {
    printf("\n============================================\n");
    printf("   STUDENT RECORD MANAGEMENT & ANALYTICS\n");
    printf("============================================\n");
    printf("1. Add Student\n");
    printf("2. Display All Students\n");
    printf("3. Search Student\n");
    printf("4. Update Student\n");
    printf("5. Delete Student\n");
    printf("6. Sort Students\n");
    printf("7. Calculate Statistics\n");
    printf("8. Save Records\n");
    printf("9. Exit\n");
    printf("============================================\n");
}
