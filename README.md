# 🎓 Student Management System — DevOps Mini-Project

A complete end-to-end DevOps pipeline built as a college mini-project.

## 📋 What This Project Does
A web application to manage student records (Add, View, Update, Delete)
with a full automated CI/CD pipeline.

## 🛠️ Technology Stack
| Layer | Tool |
|---|---|
| Application | Python + Flask |
| Version Control | Git + GitHub |
| CI/CD | Jenkins |
| Testing | PyTest |
| Containerization | Docker |
| Image Registry | Docker Hub |
| Monitoring | Prometheus |
| Dashboard | Grafana |
| Alerting | Grafana Alerts |

## 🚀 Pipeline Flow
```
Code Push → GitHub → Webhook → Jenkins →
Checkout → Install → Build → Test → Docker Build → Docker Push → Deploy →
Running App → Prometheus → Grafana → Alerts
```

## ⚡ Quick Start (Local)
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/student-management.git
cd student-management

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# or: source venv/bin/activate  (Linux/Mac)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# 5. Open browser
# http://localhost:5000
```

## 🧪 Run Tests
```bash
pytest test_app.py -v
```

## 🐳 Run with Docker
```bash
docker build -t student-management:v1 .
docker run -p 5000:5000 student-management:v1
```

## 📁 Project Structure
```
student-management/
├── app.py                  # Main Flask application
├── test_app.py             # PyTest automated tests
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build instructions
├── Jenkinsfile             # CI/CD pipeline definition
├── docker-compose.yml      # Multi-container setup (app + monitoring)
├── prometheus.yml          # Prometheus configuration
├── README.md               # This file
├── templates/
│   ├── index.html          # Home page
│   ├── students.html       # View all students
│   └── add_student.html    # Add/Edit student form
└── static/
    └── style.css           # Application styles
```

## 👥 Team
- Member 1 — Application Development, Git, Testing
- Member 2 — Jenkins, CI/CD Pipeline, Docker
- Member 3 — Prometheus, Grafana, Alerting

## 📸 Screenshots
All screenshots are in the `screenshots/` folder.

---
*Built as a DevOps mini-project. Pipeline: Dev → CI → CD → Monitor → Alert.*
