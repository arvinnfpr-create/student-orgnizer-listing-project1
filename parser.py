import re


def parse_student_text(text: str) -> dict:
    student = {
        "name": None,
        "field": None,
        "grade": None,
        "student_phone": None,
        "parent_phone": None,
    }

    patterns = {
        "name": r"👤\s*نام:\s*(.+)",
        "field": r"🎓\s*رشته:\s*(.+)",
        "grade": r"📚\s*مقطع:\s*(.+)",
        "student_phone": r"📱\s*شماره دانش‌آموز:\s*(.+)",
        "parent_phone": r"👨‍👩‍👦\s*شماره والدین:\s*(.+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text)

        if match:
            value = match.group(1).strip()
            student[field] = value

    return student


def is_valid_student(student: dict) -> bool:
    """
    Check whether the message contains
    all required student information.
    """

    return all([
        student["name"],
        student["field"],
        student["grade"],
        student["student_phone"],
        student["parent_phone"],
    ])
