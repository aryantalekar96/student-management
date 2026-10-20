# Student Management System — End-to-End DevOps Pipeline

A complete CRUD web application demonstrating DevOps automation with CI/CD,
Docker containerization, and monitoring.

## Tech Stack

| Component    | Tool              |
|-------------|-------------------|
| Language     | Python 3.14       |
| Framework    | Flask             |
| Database     | SQLite            |
| Testing      | PyTest            |
| CI/CD        | Jenkins           |
| Container    | Docker            |
| Registry     | Docker Hub        |
| Monitoring   | Prometheus        |
| Dashboards   | Grafana           |

## Quick Start

```bash
# Create virtual environment
py -3 -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Run tests
pytest test_app.py -v
```

The app will be available at **http://localhost:5000**

## Project Structure

```
student-management/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── test_app.py            # Automated tests
├── Dockerfile             # Container image definition
├── Jenkinsfile            # CI/CD pipeline
├── templates/             # HTML templates
├── static/                # CSS styles
├── monitoring/            # Prometheus & alert configs
└── docs/                  # Screenshots & report
```

## Features

- ➕ Add new students
- 📋 View all students
- ✏️ Edit student details
- 🗑️ Delete students
- ✅ Input validation
- 💾 SQLite persistence
- 🏥 Health-check endpoint (`/health`)

## License

Academic project — Experiment 10: End-to-End DevOps Pipeline
