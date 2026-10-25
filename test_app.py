"""
test_app.py — Automated Tests for Student Management System
============================================================

These tests are run automatically by Jenkins in the "Test" stage.
If ANY test fails, Jenkins STOPS the pipeline and does NOT deploy.

HOW PYTEST WORKS:
-----------------
1. PyTest looks for files named test_*.py or *_test.py
2. Inside those files, it runs every function starting with test_
3. If the function raises no errors → TEST PASSED ✅
4. If an assertion fails or an error is raised → TEST FAILED ❌

RUN THESE TESTS MANUALLY:
--------------------------
    pytest test_app.py -v

The -v flag means "verbose" — show each test name individually.
"""

import pytest
import json
import sys
import os

# Add the parent directory to Python's path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, students, next_id


# ===========================================================================
# FIXTURE: client
# ===========================================================================
# A fixture is setup code that runs before each test.
# Here we create a "test client" — a fake browser that can talk to our app.
# We also reset the students list before every test so tests don't interfere.
# ===========================================================================
@pytest.fixture
def client():
    """Create a test client with a clean state before each test."""
    app.config['TESTING'] = True  # Put Flask in test mode

    # Reset students list before each test for isolation
    students.clear()

    # Import and reset next_id too
    import app as app_module
    app_module.next_id = 1

    # Create the test client (fake browser)
    with app.test_client() as client:
        yield client  # Give the client to the test function


# ===========================================================================
# TEST 1: Home Page Loads
# ===========================================================================
def test_home_page_loads(client):
    """
    Test: GET /  should return HTTP 200 (OK) and show the home page.

    HTTP Status Codes you must know for the viva:
      200 = OK (request succeeded)
      201 = Created (new resource created)
      400 = Bad Request (client sent bad data)
      404 = Not Found (resource doesn't exist)
      500 = Internal Server Error (something crashed)
    """
    response = client.get('/')

    # assert = "I expect this to be true"
    assert response.status_code == 200, "Home page should return 200 OK"
    assert b'Student Management' in response.data, \
        "Home page should contain 'Student Management'"


# ===========================================================================
# TEST 2: Health Check Endpoint
# ===========================================================================
def test_health_check(client):
    """
    Test: GET /health should return {"status": "healthy"}
    Prometheus uses this endpoint to check if the app is UP.
    """
    response = client.get('/health')

    assert response.status_code == 200
    data = json.loads(response.data)  # Parse JSON response
    assert data['status'] == 'healthy', "Health check must return 'healthy'"


# ===========================================================================
# TEST 3: View Students Page (Empty)
# ===========================================================================
def test_view_students_empty(client):
    """
    Test: GET /students with no students should return 200 and show empty state.
    """
    response = client.get('/students')

    assert response.status_code == 200
    assert b'No students registered' in response.data, \
        "Empty students page should show empty state message"


# ===========================================================================
# TEST 4: Add Student Form Loads
# ===========================================================================
def test_add_student_form_loads(client):
    """
    Test: GET /add should show the add student form.
    """
    response = client.get('/add')

    assert response.status_code == 200
    assert b'Add' in response.data, "Add page should contain 'Add'"


# ===========================================================================
# TEST 5: API — Add a Student (POST)
# ===========================================================================
def test_api_add_student(client):
    """
    Test: POST /api/students with valid JSON should return 201 Created.
    This is the most important test — it checks the core Create operation.
    """
    # This is the JSON data we are sending (like a form submission)
    new_student = {
        "name": "Rahul Sharma",
        "age": 20,
        "course": "Computer Science"
    }

    response = client.post(
        '/api/students',
        data=json.dumps(new_student),          # Convert dict to JSON string
        content_type='application/json'         # Tell Flask it's JSON
    )

    assert response.status_code == 201, "Adding a student should return 201 Created"
    data = json.loads(response.data)
    assert data['name'] == 'Rahul Sharma', "Returned student should have the correct name"
    assert data['id'] == 1, "First student should have id=1"


# ===========================================================================
# TEST 6: API — Get All Students (GET)
# ===========================================================================
def test_api_get_students(client):
    """
    Test: POST a student, then GET all students — should return a list with 1 item.
    """
    # First add a student
    client.post(
        '/api/students',
        data=json.dumps({"name": "Priya Patel", "age": 21, "course": "IT"}),
        content_type='application/json'
    )

    # Then get all students
    response = client.get('/api/students')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1, "Should have exactly 1 student"
    assert data[0]['name'] == 'Priya Patel'


# ===========================================================================
# TEST 7: API — Get Single Student (GET by ID)
# ===========================================================================
def test_api_get_single_student(client):
    """
    Test: Add a student, then GET /api/students/1 — should return that student.
    """
    client.post(
        '/api/students',
        data=json.dumps({"name": "Amit Kumar", "age": 22, "course": "ECE"}),
        content_type='application/json'
    )

    response = client.get('/api/students/1')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Amit Kumar'
    assert data['course'] == 'ECE'


# ===========================================================================
# TEST 8: API — Get Non-Existent Student (GET — should 404)
# ===========================================================================
def test_api_get_student_not_found(client):
    """
    Test: GET /api/students/999 for a student that doesn't exist.
    Expected: 404 Not Found.
    This tests that our app handles missing data gracefully.
    """
    response = client.get('/api/students/999')

    assert response.status_code == 404, "Non-existent student should return 404"
    data = json.loads(response.data)
    assert 'error' in data, "Response should contain an 'error' key"


# ===========================================================================
# TEST 9: API — Update a Student (PUT)
# ===========================================================================
def test_api_update_student(client):
    """
    Test: Add a student, then PUT /api/students/1 to update their course.
    """
    # Add first
    client.post(
        '/api/students',
        data=json.dumps({"name": "Sneha Reddy", "age": 20, "course": "Maths"}),
        content_type='application/json'
    )

    # Update
    response = client.put(
        '/api/students/1',
        data=json.dumps({"course": "Data Science"}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['course'] == 'Data Science', "Course should be updated to Data Science"
    assert data['name'] == 'Sneha Reddy', "Name should remain unchanged"


# ===========================================================================
# TEST 10: API — Delete a Student (DELETE)
# ===========================================================================
def test_api_delete_student(client):
    """
    Test: Add a student, delete them, then confirm they are gone.
    """
    # Add
    client.post(
        '/api/students',
        data=json.dumps({"name": "Ravi Verma", "age": 23, "course": "MBA"}),
        content_type='application/json'
    )

    # Delete
    response = client.delete('/api/students/1')
    assert response.status_code == 200

    # Confirm gone
    response = client.get('/api/students/1')
    assert response.status_code == 404, "Deleted student should return 404"


# ===========================================================================
# TEST 11: API — Add Student with Missing Data (should fail gracefully)
# ===========================================================================
def test_api_add_student_missing_data(client):
    """
    Test: POST with incomplete data should return 400 Bad Request.
    This tests input validation — important for security.
    """
    incomplete_data = {"name": "No Course"}  # Missing age and course

    response = client.post(
        '/api/students',
        data=json.dumps(incomplete_data),
        content_type='application/json'
    )

    assert response.status_code == 400, "Incomplete data should return 400 Bad Request"


# ===========================================================================
# TEST 12: Multiple Students
# ===========================================================================
def test_multiple_students(client):
    """
    Test: Add 3 students, verify all 3 are returned.
    """
    students_to_add = [
        {"name": "Alice", "age": 20, "course": "CS"},
        {"name": "Bob",   "age": 21, "course": "IT"},
        {"name": "Carol", "age": 22, "course": "ECE"},
    ]

    for s in students_to_add:
        client.post('/api/students',
                    data=json.dumps(s),
                    content_type='application/json')

    response = client.get('/api/students')
    data = json.loads(response.data)

    assert len(data) == 3, "Should have exactly 3 students"
    names = [d['name'] for d in data]
    assert 'Alice' in names
    assert 'Bob' in names
    assert 'Carol' in names
