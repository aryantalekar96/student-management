"""
Automated tests for the Student Management System.

Tests cover:
  - Home page rendering
  - Adding students (valid and invalid input)
  - Viewing student list
  - Updating student records
  - Deleting student records
  - Health-check endpoint
  - Non-existent student handling
  - Input validation edge cases

Each test uses an isolated temporary database so that no test affects
another and the real application database is never touched.
"""

import os
import tempfile
import pytest
from app import app


# ---------------------------------------------------------------------------
# Fixtures — reusable setup that runs before each test
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a test client with an isolated temporary database.

    Explanation for beginners:
    - A 'fixture' is setup code that pytest runs before each test.
    - We create a brand-new temporary database file for every test.
    - We set app.config['DATABASE'] so get_db() uses the temp path.
    - Flask's 'test_client()' lets us send HTTP requests without starting
      a real server.
    - After the test, the temp file is cleaned up automatically.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app.config["TESTING"] = True
    app.config["DATABASE"] = db_path      # ← override per-test

    with app.test_client() as client:
        with app.app_context():
            from app import init_db
            init_db()
        yield client

    # Cleanup: close the file handle and delete the temp db
    os.close(db_fd)
    os.unlink(db_path)



def add_sample_student(client, name="Test Student", email="test@example.com",
                       course="Computer Science"):
    """Helper: add a student and return the response."""
    return client.post("/add", data={
        "name": name,
        "email": email,
        "course": course,
    }, follow_redirects=True)


# ---------------------------------------------------------------------------
# Test: Home Page
# ---------------------------------------------------------------------------

class TestHomePage:
    """Tests for the home/landing page."""

    def test_home_page_loads(self, client):
        """The home page should return HTTP 200 and contain the app title."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Student Management System" in response.data

    def test_home_page_has_navigation(self, client):
        """The home page should have links to add and view students."""
        response = client.get("/")
        assert b"Add" in response.data or b"add" in response.data
        assert b"Student" in response.data


# ---------------------------------------------------------------------------
# Test: Add Student
# ---------------------------------------------------------------------------

class TestAddStudent:
    """Tests for creating new student records."""

    def test_add_page_loads(self, client):
        """The add-student form page should return HTTP 200."""
        response = client.get("/add")
        assert response.status_code == 200
        assert b"Add" in response.data

    def test_add_valid_student(self, client):
        """Adding a student with valid data should succeed and show the student."""
        response = add_sample_student(client, "Priya Patel",
                                      "priya@university.edu", "Data Science")
        assert response.status_code == 200
        assert b"Priya Patel" in response.data
        assert b"added successfully" in response.data

    def test_add_student_redirects_to_list(self, client):
        """After adding, user should be redirected to the student list."""
        response = client.post("/add", data={
            "name": "Amit Kumar",
            "email": "amit@test.com",
            "course": "Mechanical",
        }, follow_redirects=False)
        assert response.status_code == 302
        assert "/students" in response.headers["Location"]

    def test_add_multiple_students(self, client):
        """Multiple students should all appear in the list."""
        add_sample_student(client, "Student A", "a@test.com", "CS")
        add_sample_student(client, "Student B", "b@test.com", "IT")
        response = client.get("/students")
        assert b"Student A" in response.data
        assert b"Student B" in response.data


# ---------------------------------------------------------------------------
# Test: Input Validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    """Tests for form validation and error handling."""

    def test_empty_name_rejected(self, client):
        """Submitting an empty name should return an error."""
        response = client.post("/add", data={
            "name": "",
            "email": "test@example.com",
            "course": "CS",
        }, follow_redirects=True)
        assert response.status_code == 400
        assert b"Name is required" in response.data

    def test_empty_email_rejected(self, client):
        """Submitting an empty email should return an error."""
        response = client.post("/add", data={
            "name": "Valid Name",
            "email": "",
            "course": "CS",
        }, follow_redirects=True)
        assert response.status_code == 400
        assert b"Email is required" in response.data

    def test_invalid_email_rejected(self, client):
        """An invalid email format should be rejected."""
        response = client.post("/add", data={
            "name": "Valid Name",
            "email": "not-an-email",
            "course": "CS",
        }, follow_redirects=True)
        assert response.status_code == 400
        assert b"valid email" in response.data

    def test_empty_course_rejected(self, client):
        """Submitting an empty course should return an error."""
        response = client.post("/add", data={
            "name": "Valid Name",
            "email": "test@example.com",
            "course": "",
        }, follow_redirects=True)
        assert response.status_code == 400
        assert b"Course is required" in response.data

    def test_short_name_rejected(self, client):
        """A single-character name should be rejected."""
        response = client.post("/add", data={
            "name": "A",
            "email": "test@example.com",
            "course": "CS",
        }, follow_redirects=True)
        assert response.status_code == 400
        assert b"at least 2 characters" in response.data

    def test_all_fields_empty(self, client):
        """All empty fields should return multiple errors."""
        response = client.post("/add", data={
            "name": "",
            "email": "",
            "course": "",
        }, follow_redirects=True)
        assert response.status_code == 400
        assert b"Name is required" in response.data
        assert b"Email is required" in response.data
        assert b"Course is required" in response.data


# ---------------------------------------------------------------------------
# Test: View Students
# ---------------------------------------------------------------------------

class TestViewStudents:
    """Tests for the student listing page."""

    def test_students_page_loads_empty(self, client):
        """The students page should work even when empty."""
        response = client.get("/students")
        assert response.status_code == 200
        assert b"No students yet" in response.data

    def test_students_page_shows_records(self, client):
        """After adding students, they should appear on the list page."""
        add_sample_student(client, "Visible Student", "vis@test.com", "ECE")
        response = client.get("/students")
        assert response.status_code == 200
        assert b"Visible Student" in response.data
        assert b"vis@test.com" in response.data
        assert b"ECE" in response.data


# ---------------------------------------------------------------------------
# Test: Update Student
# ---------------------------------------------------------------------------

class TestUpdateStudent:
    """Tests for editing existing student records."""

    def test_edit_page_loads(self, client):
        """The edit page should load with existing student data."""
        add_sample_student(client, "Edit Me", "edit@test.com", "Physics")
        response = client.get("/edit/1")
        assert response.status_code == 200
        assert b"Edit Me" in response.data
        assert b"edit@test.com" in response.data

    def test_update_student_succeeds(self, client):
        """Updating a student's details should reflect in the list."""
        add_sample_student(client, "Old Name", "old@test.com", "Old Course")
        response = client.post("/edit/1", data={
            "name": "New Name",
            "email": "new@test.com",
            "course": "New Course",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"New Name" in response.data
        assert b"updated successfully" in response.data

    def test_update_with_invalid_data(self, client):
        """Updating with invalid data should show errors."""
        add_sample_student(client, "Valid Name", "valid@test.com", "CS")
        response = client.post("/edit/1", data={
            "name": "",
            "email": "valid@test.com",
            "course": "CS",
        }, follow_redirects=True)
        assert response.status_code == 400
        assert b"Name is required" in response.data

    def test_edit_nonexistent_student(self, client):
        """Editing a student that doesn't exist should redirect with error."""
        response = client.get("/edit/999", follow_redirects=True)
        assert response.status_code == 200
        assert b"not found" in response.data


# ---------------------------------------------------------------------------
# Test: Delete Student
# ---------------------------------------------------------------------------

class TestDeleteStudent:
    """Tests for deleting student records."""

    def test_delete_student_succeeds(self, client):
        """Deleting a student should remove them from the list."""
        add_sample_student(client, "Delete Me", "del@test.com", "Chemistry")
        response = client.post("/delete/1", follow_redirects=True)
        assert response.status_code == 200
        assert b"deleted successfully" in response.data
        assert b"Delete Me" not in response.data

    def test_delete_nonexistent_student(self, client):
        """Deleting a student that doesn't exist should show an error."""
        response = client.post("/delete/999", follow_redirects=True)
        assert response.status_code == 200
        assert b"not found" in response.data

    def test_delete_only_removes_target(self, client):
        """Deleting one student should not affect others."""
        add_sample_student(client, "Keep Me", "keep@test.com", "CS")
        add_sample_student(client, "Remove Me", "remove@test.com", "IT")
        client.post("/delete/2", follow_redirects=True)
        response = client.get("/students")
        assert b"Keep Me" in response.data
        assert b"Remove Me" not in response.data


# ---------------------------------------------------------------------------
# Test: Health Check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    """Tests for the /health monitoring endpoint."""

    def test_health_returns_ok(self, client):
        """The health endpoint should return a healthy JSON status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"


# ---------------------------------------------------------------------------
# Test: HTTP Methods
# ---------------------------------------------------------------------------

class TestHTTPMethods:
    """Tests for correct HTTP method handling."""

    def test_delete_requires_post(self, client):
        """DELETE route should reject GET requests (method not allowed)."""
        add_sample_student(client)
        response = client.get("/delete/1")
        assert response.status_code == 405

    def test_add_get_shows_form(self, client):
        """GET /add should show the form, not process a submission."""
        response = client.get("/add")
        assert response.status_code == 200
        assert b"<form" in response.data
