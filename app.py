"""
Student Management System — Flask Application
Provides CRUD operations for managing student records using SQLite.
"""

import os
import re
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# ---------------------------------------------------------------------------
# Application factory-style setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

# Database file path stored in app.config so tests can override it per-test.
# Reading it dynamically (not as a module-level constant) ensures isolation.
app.config["DATABASE"] = os.environ.get(
    "DATABASE_PATH", os.path.join(app.root_path, "students.db")
)

# ---------------------------------------------------------------------------
# Prometheus metrics setup
# ---------------------------------------------------------------------------
REQUEST_COUNT = Counter(
    "flask_http_request_total",
    "Total HTTP requests processed by Flask application",
    ["method", "status"],
)

@app.after_request
def record_metrics(response):
    if request.path != "/metrics":
        REQUEST_COUNT.labels(method=request.method, status=str(response.status_code)).inc()
    return response


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    """Return a database connection for the current request.

    Connections are stored on Flask's `g` object so that every function
    within the same request shares the same connection, and it is closed
    automatically when the request ends.

    The database path is read from app.config["DATABASE"] each time so
    that tests can override it per-test without reimporting the module.
    """
    if "db" not in g:
        db_path = app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row          # rows behave like dicts
        g.db.execute("PRAGMA journal_mode=WAL")  # safer concurrent reads
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Close the database connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the students table if it does not already exist."""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            email   TEXT    NOT NULL,
            course  TEXT    NOT NULL
        )
    """)
    db.commit()


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_student(name: str, email: str, course: str) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors: list[str] = []
    if not name or not name.strip():
        errors.append("Name is required.")
    elif len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters.")
    if not email or not email.strip():
        errors.append("Email is required.")
    elif not EMAIL_RE.match(email.strip()):
        errors.append("Please enter a valid email address.")
    if not course or not course.strip():
        errors.append("Course is required.")
    return errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@app.route("/students")
def students():
    """Display all student records."""
    db = get_db()
    all_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    return render_template("students.html", students=all_students)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    """Show the add-student form (GET) or process it (POST)."""
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        course = request.form.get("course", "")

        errors = validate_student(name, email, course)
        if errors:
            for err in errors:
                flash(err, "error")
            return render_template(
                "add_student.html",
                name=name, email=email, course=course
            ), 400

        db = get_db()
        db.execute(
            "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
            (name.strip(), email.strip(), course.strip()),
        )
        db.commit()
        flash("Student added successfully!", "success")
        return redirect(url_for("students"))

    return render_template("add_student.html")


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    """Edit an existing student record."""
    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        course = request.form.get("course", "")

        errors = validate_student(name, email, course)
        if errors:
            for err in errors:
                flash(err, "error")
            return render_template(
                "edit_student.html",
                student={"id": student_id, "name": name,
                         "email": email, "course": course},
            ), 400

        db.execute(
            "UPDATE students SET name = ?, email = ?, course = ? WHERE id = ?",
            (name.strip(), email.strip(), course.strip(), student_id),
        )
        db.commit()
        flash("Student updated successfully!", "success")
        return redirect(url_for("students"))

    return render_template("edit_student.html", student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    """Delete a student record."""
    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash("Student deleted successfully!", "success")
    return redirect(url_for("students"))


@app.route("/health")
def health():
    """Health-check endpoint for monitoring (Prometheus / deployment)."""
    try:
        db = get_db()
        db.execute("SELECT 1")
        return {"status": "healthy"}, 200
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}, 500


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# ---------------------------------------------------------------------------
# Application startup
# ---------------------------------------------------------------------------

# Ensure the table exists on first import / startup.
with app.app_context():
    init_db()

if __name__ == "__main__":
    # 0.0.0.0 so the app is reachable from outside Docker containers.
    app.run(host="0.0.0.0", port=5000, debug=True)
