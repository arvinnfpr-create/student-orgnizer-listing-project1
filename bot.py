import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
from openpyxl import Workbook

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from parser import parse_student_text, is_valid_student

from database import (
    init_database,
    add_student,
    get_students,
    get_student_count,
    clear_students,
)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


# =========================
# Render Health Server
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return


def run_health_server():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


# =========================
# Telegram Commands
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    count = get_student_count()

    await update.message.reply_text(
        "سلام 👋\n\n"
        "ربات مدیریت دانش‌آموزان آماده است.\n\n"
        "📥 پیام‌های دانش‌آموزان را برای من فوروارد کنید.\n"
        "اطلاعات هر دانش‌آموز به صورت خودکار ذخیره می‌شود.\n\n"
        "بعد از اینکه تمام پیام‌ها را فرستادید:\n"
        "/export\n\n"
        f"📊 تعداد ذخیره‌شده فعلی: {count}"
    )


async def receive_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not text:
        return

    # Parse student information
    student = parse_student_text(text)

    # Check required fields
    if not is_valid_student(student):

        await update.message.reply_text(
            "❌ این پیام اطلاعات کامل دانش‌آموز را ندارد.\n\n"
            "اطمینان حاصل کنید پیام شامل این موارد باشد:\n"
            "👤 نام\n"
            "🎓 رشته\n"
            "📚 مقطع\n"
            "📱 شماره دانش‌آموز\n"
            "👨‍👩‍👦 شماره والدین"
        )

        return

    # Save immediately to database
    add_student(student)

    count = get_student_count()

    await update.message.reply_text(
        "✅ اطلاعات دانش‌آموز ذخیره شد.\n\n"
        f"👤 {student['name']}\n"
        f"🎓 {student['field']}\n"
        f"📚 {student['grade']}\n"
        f"📱 شماره دانش‌آموز: {student['student_phone']}\n"
        f"👨‍👩‍👦 شماره والدین: {student['parent_phone']}\n\n"
        f"📊 تعداد کل ذخیره‌شده: {count}"
    )


async def export_excel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    students = get_students()

    if not students:

        await update.message.reply_text(
            "❌ هنوز هیچ اطلاعاتی دریافت نشده است."
        )

        return

    # Create Excel workbook
    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Students"

    # Headers
    sheet.append([
        "نام و نام خانوادگی",
        "پایه و رشته",
        "شماره دانش‌آموز",
        "شماره والدین",
    ])

    # Add students
    for student in students:

        grade_and_field = (
            f"{student['grade']} - {student['field']}"
        )

        sheet.append([
            student["name"],
            grade_and_field,
            student["student_phone"],
            student["parent_phone"],
        ])

    # Column widths
    sheet.column_dimensions["A"].width = 30
    sheet.column_dimensions["B"].width = 25
    sheet.column_dimensions["C"].width = 20
    sheet.column_dimensions["D"].width = 20

    # Save Excel
    file_path = "students.xlsx"

    workbook.save(file_path)

    # Send Excel
    with open(file_path, "rb") as file:

        await update.message.reply_document(
            document=file,
            filename="students.xlsx",
            caption=(
                "📊 فایل اکسل آماده شد.\n\n"
                f"👥 تعداد دانش‌آموزان: {len(students)}"
            ),
        )


async def clear_database(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    count = get_student_count()

    if count == 0:

        await update.message.reply_text(
            "ℹ️ دیتابیس خالی است."
        )

        return

    clear_students()

    await update.message.reply_text(
        "🗑 تمام اطلاعات پاک شد.\n\n"
        f"تعداد رکوردهای حذف‌شده: {count}"
    )


# =========================
# Main
# =========================

def main():

    # Start Render health server
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    health_thread.start()

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN پیدا نشد. فایل .env را بررسی کنید."
        )

    # Initialize database
    init_database()

    # Create Telegram application
    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # /export
    app.add_handler(
        CommandHandler("export", export_excel)
    )

    # /clear
    app.add_handler(
        CommandHandler("clear", clear_database)
    )

    # Normal text messages
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_message
        )
    )

    print("Bot is running...")

    # Start Telegram polling
    app.run_polling()


if __name__ == "__main__":
    main()