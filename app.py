"""
Student Management System
=========================
A simple Flask web application to manage student records.
Supports: Add, View, Update, Delete (CRUD operations).

This file is the HEART of the application.
Flask reads this file and starts a web server.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify

# --------------------------------------------------------------------------
# Create the Flask application object.
# __name__ tells Flask where to look for templates and static files.
# --------------------------------------------------------------------------
app = Flask(__name__)

# --------------------------------------------------------------------------
# In-memory storage: a simple Python list of dictionaries.
# Each student is a dict with id, name, age, course.
# In a real project you would use a database (like MySQL or PostgreSQL).
# For this mini-project, a list is enough to show the DevOps pipeline.
# --------------------------------------------------------------------------
students = []
next_id = 1  # Auto-increment ID counter


# --------------------------------------------------------------------------
# ROUTE 1: Home Page
# URL  : http://localhost:5000/
# GET  : Show the home page with navigation links.
# --------------------------------------------------------------------------
@app.route('/')
def index():
    """Home page — shows navigation links."""
    return render_template('index.html')


# --------------------------------------------------------------------------
# ROUTE 2: View All Students
# URL  : http://localhost:5000/students
# GET  : Show all students in a table.
# --------------------------------------------------------------------------
@app.route('/students')
def view_students():
    """Show all students in a table."""
    return render_template('students.html', students=students)


# --------------------------------------------------------------------------
# ROUTE 3: Add a Student
# URL  : http://localhost:5000/add
# GET  : Show the add-student form.
# POST : Receive the form data and save the new student.
# --------------------------------------------------------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """Show form (GET) or save new student (POST)."""
    global next_id
    if request.method == 'POST':
        # Read values the user typed into the form
        name   = request.form.get('name', '').strip()
        age    = request.form.get('age', '').strip()
        course = request.form.get('course', '').strip()

        # Basic validation — do not save empty records
        if name and age and course:
            student = {
                'id'    : next_id,
                'name'  : name,
                'age'   : int(age),
                'course': course
            }
            students.append(student)
            next_id += 1

        # After saving, redirect to the students list
        return redirect(url_for('view_students'))

    # If it's a GET request, just show the empty form
    return render_template('add_student.html')


# --------------------------------------------------------------------------
# ROUTE 4: Update a Student
# URL  : http://localhost:5000/update/<id>
# GET  : Show the edit form pre-filled with current data.
# POST : Save the updated data.
# --------------------------------------------------------------------------
@app.route('/update/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    """Show edit form (GET) or save changes (POST)."""
    # Find the student with the matching id
    student = next((s for s in students if s['id'] == student_id), None)

    if student is None:
        return "Student not found", 404

    if request.method == 'POST':
        # Update only fields that were filled in
        student['name']   = request.form.get('name', student['name']).strip()
        student['age']    = int(request.form.get('age', student['age']))
        student['course'] = request.form.get('course', student['course']).strip()
        return redirect(url_for('view_students'))

    return render_template('add_student.html', student=student)


# --------------------------------------------------------------------------
# ROUTE 5: Delete a Student
# URL  : http://localhost:5000/delete/<id>
# GET  : Remove the student and redirect back to the list.
# --------------------------------------------------------------------------
@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    """Delete a student by ID."""
    global students
    students = [s for s in students if s['id'] != student_id]
    return redirect(url_for('view_students'))


# --------------------------------------------------------------------------
# ROUTE 6: Health Check (used by Prometheus and Jenkins to verify the app)
# URL  : http://localhost:5000/health
# Returns a JSON response: {"status": "healthy"}
# Prometheus will call this URL every few seconds to confirm the app is UP.
# --------------------------------------------------------------------------
@app.route('/health')
def health():
    """Health check endpoint — returns JSON status."""
    return jsonify({"status": "healthy", "students_count": len(students)}), 200


# --------------------------------------------------------------------------
# ROUTE 7: API Endpoints (for Postman tests and PyTest)
# These routes return JSON instead of HTML pages.
# Useful for automated testing without a browser.
# --------------------------------------------------------------------------
@app.route('/api/students', methods=['GET'])
def api_get_students():
    """Return all students as JSON."""
    return jsonify(students), 200


@app.route('/api/students', methods=['POST'])
def api_add_student():
    """Add a student via JSON (used by automated tests)."""
    global next_id
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name   = data.get('name', '').strip()
    age    = data.get('age')
    course = data.get('course', '').strip()

    if not name or not age or not course:
        return jsonify({"error": "name, age and course are required"}), 400

    student = {'id': next_id, 'name': name, 'age': int(age), 'course': course}
    students.append(student)
    next_id += 1
    return jsonify(student), 201


@app.route('/api/students/<int:student_id>', methods=['GET'])
def api_get_student(student_id):
    """Return one student as JSON."""
    student = next((s for s in students if s['id'] == student_id), None)
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200


@app.route('/api/students/<int:student_id>', methods=['PUT'])
def api_update_student(student_id):
    """Update a student via JSON."""
    student = next((s for s in students if s['id'] == student_id), None)
    if student is None:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()
    if data.get('name'):
        student['name'] = data['name']
    if data.get('age'):
        student['age'] = int(data['age'])
    if data.get('course'):
        student['course'] = data['course']
    return jsonify(student), 200


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def api_delete_student(student_id):
    """Delete a student via JSON API."""
    global students
    student = next((s for s in students if s['id'] == student_id), None)
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    students = [s for s in students if s['id'] != student_id]
    return jsonify({"message": "Student deleted"}), 200


# --------------------------------------------------------------------------
# Start the application.
# debug=True  → auto-reloads when you save the file (development only).
# host='0.0.0.0' → makes the app accessible from outside the container too.
# port=5000   → the app listens on port 5000.
# --------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
