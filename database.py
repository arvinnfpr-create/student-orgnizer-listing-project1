import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not found in .env")

    return psycopg2.connect(DATABASE_URL)


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            field TEXT NOT NULL,
            grade TEXT NOT NULL,
            student_phone TEXT NOT NULL,
            parent_phone TEXT NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


def add_student(student: dict):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students (
            name,
            field,
            grade,
            student_phone,
            parent_phone
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        student["name"],
        student["field"],
        student["grade"],
        student["student_phone"],
        student["parent_phone"],
    ))

    connection.commit()
    cursor.close()
    connection.close()


def get_students():
    connection = get_connection()
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

    cursor.close()
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
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")

    count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return count


def clear_students():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM students")

    connection.commit()
    cursor.close()
    connection.close()