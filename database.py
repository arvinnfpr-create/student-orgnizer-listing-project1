import sqlite3


DATABASE_FILE = "students.db"


def init_database():
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            field TEXT NOT NULL,
            grade TEXT NOT NULL,
            student_phone TEXT NOT NULL,
            parent_phone TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_student(student: dict):
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students (
            name,
            field,
            grade,
            student_phone,
            parent_phone
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        student["name"],
        student["field"],
        student["grade"],
        student["student_phone"],
        student["parent_phone"],
    ))

    connection.commit()
    connection.close()


def get_students():
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            name,
            field,
            grade,
            student_phone,
            parent_phone
        FROM students
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    students = []

    for row in rows:
        students.append({
            "name": row[0],
            "field": row[1],
            "grade": row[2],
            "student_phone": row[3],
            "parent_phone": row[4],
        })

    return students


def get_student_count():
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")

    count = cursor.fetchone()[0]

    connection.close()

    return count


def clear_students():
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute("DELETE FROM students")

    connection.commit()
    connection.close()
