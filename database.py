import sqlite3
from typing import List, Optional, Dict, Any

DB_NAME = "university.db"


def get_connection(db_name: str = DB_NAME) -> sqlite3.Connection:
    """Connect to SQLite database with FK constraint support."""
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_name: str = DB_NAME) -> None:
    """Create students, courses, and student_courses tables."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        # Table 1: students
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                major TEXT NOT NULL
            );
        """)

        # Table 2: courses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                instructor TEXT NOT NULL
            );
        """)

        # Table 3: Many-To-Many linking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_courses (
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
            );
        """)
        conn.commit()
    finally:
        conn.close()


# --- Student Operations ---

def add_student(name: str, age: int, major: str, db_name: str = DB_NAME) -> int:
    """Add a new student."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, age, major) VALUES (?, ?, ?);",
            (name, age, major)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_students(db_name: str = DB_NAME) -> List[Dict[str, Any]]:
    """Retrieve all students."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY id;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_student_by_id(student_id: int, db_name: str = DB_NAME) -> Optional[Dict[str, Any]]:
    """Retrieve student by ID."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?;", (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_student(student_id: int, name: str, age: int, major: str, db_name: str = DB_NAME) -> bool:
    """Update existing student info."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, age = ?, major = ? WHERE id = ?;",
            (name, age, major, student_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_student(student_id: int, db_name: str = DB_NAME) -> bool:
    """Delete student by ID."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?;", (student_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# --- Course Operations ---

def add_course(course_name: str, instructor: str, db_name: str = DB_NAME) -> int:
    """Add a new course."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO courses (course_name, instructor) VALUES (?, ?);",
            (course_name, instructor)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_courses(db_name: str = DB_NAME) -> List[Dict[str, Any]]:
    """Retrieve all courses."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY course_id;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_course_by_id(course_id: int, db_name: str = DB_NAME) -> Optional[Dict[str, Any]]:
    """Retrieve course by ID."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE course_id = ?;", (course_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_course(course_id: int, course_name: str, instructor: str, db_name: str = DB_NAME) -> bool:
    """Update existing course info."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE courses SET course_name = ?, instructor = ? WHERE course_id = ?;",
            (course_name, instructor, course_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_course(course_id: int, db_name: str = DB_NAME) -> bool:
    """Delete course by ID."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE course_id = ?;", (course_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# --- Enrollment Operations (Many-To-Many) ---

def enroll_student(student_id: int, course_id: int, db_name: str = DB_NAME) -> bool:
    """Enroll a student in a course."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO student_courses (student_id, course_id) VALUES (?, ?);",
            (student_id, course_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def unenroll_student(student_id: int, course_id: int, db_name: str = DB_NAME) -> bool:
    """Remove student enrollment from a course."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM student_courses WHERE student_id = ? AND course_id = ?;",
            (student_id, course_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_students_in_course(course_id: int, db_name: str = DB_NAME) -> List[Dict[str, Any]]:
    """Get all students registered for a specific course using SQL JOIN query."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.name, s.age, s.major
            FROM students s
            JOIN student_courses sc ON s.id = sc.student_id
            WHERE sc.course_id = ?
            ORDER BY s.id;
        """, (course_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_courses_for_student(student_id: int, db_name: str = DB_NAME) -> List[Dict[str, Any]]:
    """Get all courses a student is enrolled in using SQL JOIN query."""
    conn = get_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.course_id, c.course_name, c.instructor
            FROM courses c
            JOIN student_courses sc ON c.course_id = sc.course_id
            WHERE sc.student_id = ?
            ORDER BY c.course_id;
        """, (student_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def seed_sample_data(db_name: str = DB_NAME) -> None:
    """Populate database with sample initial data if empty."""
    if get_all_students(db_name) or get_all_courses(db_name):
        return

    s1 = add_student("Олександр Коваленко", 20, "Комп'ютерні науки", db_name)
    s2 = add_student("Марія Шевченко", 21, "Інженерія програмного забезпечення", db_name)
    s3 = add_student("Дмитро Бондаренко", 19, "Кібербезпека", db_name)
    s4 = add_student("Анна Мельник", 22, "Прикладна математика", db_name)

    c1 = add_course("Бази даних та SQL", "проф. Сидоренко В.П.", db_name)
    c2 = add_course("Алгоритми та структури даних", "доц. Петренко О.І.", db_name)
    c3 = add_course("Веб-розробка на Python", "викл. Ковальчук Н.М.", db_name)

    enroll_student(s1, c1, db_name)
    enroll_student(s1, c2, db_name)
    enroll_student(s2, c1, db_name)
    enroll_student(s2, c3, db_name)
    enroll_student(s3, c2, db_name)
    enroll_student(s4, c1, db_name)
    enroll_student(s4, c3, db_name)
