# Experiment 10: Mini-Project — End-to-End DevOps Pipeline

## Student Management System with End-to-End DevOps Automation

---

## 1. Project Title

**Student Management System with End-to-End DevOps Automation**

---

## 2. Abstract

This project implements an end-to-end DevOps pipeline for a Student Management System web application. The application provides full CRUD (Create, Read, Update, Delete) functionality for managing student records, built using Python Flask with SQLite as the database. The project demonstrates the complete DevOps lifecycle — from source code management using Git and GitHub, through automated testing with PyTest, continuous integration and continuous deployment via Jenkins pipelines, Docker containerization with Docker Hub image registry, to production monitoring using Prometheus and Grafana dashboards with alerting. The primary objective is to demonstrate how modern DevOps practices automate the software delivery process, improve code quality through automated testing, ensure consistent deployment through containerization, and maintain system reliability through real-time monitoring and alerting.

---

## 3. Introduction

In modern software development, writing code is only one part of delivering a working product. Code must be tested, packaged, deployed, and monitored — and these steps must happen reliably and repeatedly for every change. DevOps is the set of practices and tools that automates this entire lifecycle.

This project takes a simple but functional web application — a Student Management System — and wraps it in a complete DevOps pipeline. Every push to the source code repository triggers an automated sequence: the code is checked out, dependencies are installed, tests are run, a Docker container is built, the image is pushed to a registry, the application is deployed, and monitoring confirms it is running correctly.

By implementing this pipeline, we demonstrate that DevOps is not a single tool but an integrated workflow where each component (version control, CI/CD, containerization, monitoring) serves a specific purpose in delivering reliable software.

---

## 4. Problem Statement

Manual software deployment is error-prone, slow, and unreliable. Without automation:

- Code changes are tested inconsistently or not at all.
- Deployment steps are performed manually, introducing human error.
- The application environment differs between development and production ("it works on my machine" problem).
- There is no visibility into whether the deployed application is healthy.
- Rollbacks after a failed deployment are difficult and time-consuming.

This project addresses these problems by implementing an automated pipeline that tests, packages, deploys, and monitors the application with minimal manual intervention.

---

## 5. Objectives

1. Develop a functional Student Management System with CRUD operations.
2. Implement version control using Git with GitHub as the remote repository.
3. Write automated tests using PyTest to validate application correctness.
4. Create a Docker container for consistent, portable deployment.
5. Configure a Jenkins CI/CD pipeline that automates build, test, and deploy.
6. Integrate GitHub webhooks to trigger the pipeline on every code push.
7. Push Docker images to Docker Hub as a central image registry.
8. Set up Prometheus monitoring with system and application metrics.
9. Create Grafana dashboards for visual monitoring.
10. Configure alerts for critical conditions (e.g., application downtime).

---

## 6. Scope

### In Scope
- Web application with full CRUD for student records
- SQLite database for data persistence
- Git version control with GitHub hosting
- Automated unit and integration testing
- Jenkins declarative pipeline with multiple stages
- Docker containerization and Docker Hub publishing
- Prometheus metrics collection
- Grafana dashboard visualization
- Basic alerting rules

### Out of Scope
- Cloud deployment (AWS, GCP, Azure)
- Kubernetes orchestration
- Database migration tools
- User authentication and authorization
- Load balancing or high availability
- Production-grade security hardening

---

## 7. Target Users

- **Primary:** College evaluators and examiners assessing DevOps knowledge
- **Secondary:** Engineering students learning DevOps practices
- **Application users:** Administrative staff managing student records (hypothetical)

---

## 8. Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-01 | Add a new student with name, email, and course | Must Have |
| FR-02 | View a list of all students | Must Have |
| FR-03 | Update an existing student's details | Must Have |
| FR-04 | Delete a student record | Must Have |
| FR-05 | Display a clean, usable home page | Must Have |
| FR-06 | Validate user inputs (no empty fields, valid email) | Must Have |
| FR-07 | Persist records in SQLite database | Must Have |
| FR-08 | Display appropriate error and success messages | Must Have |
| FR-09 | Return proper HTTP status codes for all operations | Should Have |
| FR-10 | Handle requests for non-existent student records | Should Have |

---

## 9. Non-Functional Requirements

| ID | Requirement | Category |
|----|------------|----------|
| NFR-01 | Application must start within 5 seconds | Performance |
| NFR-02 | Application must respond to requests within 500ms | Performance |
| NFR-03 | All automated tests must pass before deployment | Quality |
| NFR-04 | Docker image must be under 200 MB | Efficiency |
| NFR-05 | Pipeline must complete within 5 minutes | Efficiency |
| NFR-06 | Application must be accessible on the configured port | Availability |
| NFR-07 | Database must persist across application restarts | Reliability |
| NFR-08 | No secrets stored in source code or screenshots | Security |
| NFR-09 | Source code must follow PEP 8 conventions | Maintainability |
| NFR-10 | Monitoring must detect application downtime within 30s | Observability |

---

## 10. Proposed System

The proposed system consists of two integrated parts:

**Application Layer:** A Python Flask web application providing a browser-based interface for managing student records. Data is stored in a SQLite database. The application exposes HTML pages for user interaction and can also serve as a simple REST-like API.

**DevOps Pipeline Layer:** An automated pipeline that takes the application from source code to monitored deployment:

1. Developer pushes code to GitHub.
2. GitHub webhook notifies Jenkins.
3. Jenkins checks out the code, installs dependencies, and runs tests.
4. If tests pass, Jenkins builds a Docker image and pushes it to Docker Hub.
5. Jenkins deploys the new container, replacing the old one.
6. Prometheus scrapes metrics from the running application and host.
7. Grafana displays these metrics on dashboards.
8. Alert rules notify when the application is unhealthy.

---

## 11. Technology Stack

| Layer | Tool | Version | Justification |
|-------|------|---------|---------------|
| Language | Python | 3.14 | Widely used, beginner-friendly, rich ecosystem |
| Web Framework | Flask | Latest | Lightweight, minimal boilerplate, ideal for small apps |
| Database | SQLite | Built-in | Zero-configuration, file-based, no separate server needed |
| Templating | Jinja2 | (with Flask) | Flask's default template engine for HTML rendering |
| Styling | CSS | — | Simple styling without additional build tools |
| Version Control | Git | 2.53 | Industry-standard distributed version control |
| Code Hosting | GitHub | — | Free hosting, webhooks, widely used in industry |
| Testing | PyTest | Latest | Simple syntax, powerful features, standard Python testing |
| CI/CD Server | Jenkins | Latest | Open-source, extensible, declarative pipeline support |
| Containerization | Docker | Latest | Industry-standard container platform |
| Image Registry | Docker Hub | — | Free public/private image hosting |
| Monitoring | Prometheus | Latest | Pull-based metrics, powerful query language (PromQL) |
| System Metrics | Windows Exporter | Latest | Exposes Windows host metrics to Prometheus |
| Dashboards | Grafana | Latest | Rich visualization, Prometheus integration |

---

## 12. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DEVELOPMENT ENVIRONMENT                         │
│                                                                        │
│  ┌──────────┐    git push    ┌──────────┐    webhook    ┌──────────┐  │
│  │Developer │ ──────────────►│  GitHub   │─────────────►│ Jenkins  │  │
│  │(VS Code) │                │Repository │              │  Server  │  │
│  └──────────┘                └──────────┘              └────┬─────┘  │
│                                                              │        │
│                              CI/CD PIPELINE                  │        │
│                    ┌─────────────────────────────┐           │        │
│                    │  1. Checkout Code            │◄──────────┘        │
│                    │  2. Install Dependencies     │                    │
│                    │  3. Run PyTest Tests         │                    │
│                    │  4. Build Docker Image       │                    │
│                    │  5. Push to Docker Hub       │                    │
│                    │  6. Deploy Container         │                    │
│                    └──────────────┬──────────────┘                    │
│                                   │                                    │
│                    ┌──────────────▼──────────────┐                    │
│                    │     DEPLOYMENT TARGET        │                    │
│                    │  ┌────────────────────────┐  │                    │
│                    │  │   Docker Container     │  │                    │
│                    │  │  ┌──────────────────┐  │  │                    │
│                    │  │  │ Flask App (:5001) │  │  │                    │
│                    │  │  │ + SQLite DB       │  │  │                    │
│                    │  │  └──────────────────┘  │  │                    │
│                    │  └────────────────────────┘  │                    │
│                    └──────────────┬──────────────┘                    │
│                                   │                                    │
│                    MONITORING & OBSERVABILITY                          │
│                    ┌──────────────▼──────────────┐                    │
│                    │  Prometheus (:9090)          │                    │
│                    │  ◄── scrapes ── Win Exporter │                    │
│                    │  ◄── scrapes ── Flask App    │                    │
│                    └──────────────┬──────────────┘                    │
│                                   │                                    │
│                    ┌──────────────▼──────────────┐                    │
│                    │  Grafana (:3000)             │                    │
│                    │  Dashboards + Alerts         │                    │
│                    └─────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 13. End-to-End Workflow

```
Developer writes code
        │
        ▼
   git add + commit
        │
        ▼
    git push to GitHub ──────────────────────────┐
        │                                         │
        ▼                                         ▼
  Code visible on GitHub              GitHub sends webhook
                                              │
                                              ▼
                                     Jenkins receives trigger
                                              │
                                 ┌────────────┴────────────┐
                                 │     PIPELINE STAGES     │
                                 ├─────────────────────────┤
                                 │ 1. Checkout source code │
                                 │ 2. Install dependencies │
                                 │ 3. Run pytest tests     │
                                 │    ├─ FAIL → Stop here  │
                                 │    └─ PASS → Continue   │
                                 │ 4. Build Docker image   │
                                 │ 5. Push to Docker Hub   │
                                 │ 6. Deploy container     │
                                 └────────────┬────────────┘
                                              │
                                              ▼
                                   Application running
                                   on Docker (:5001)
                                              │
                                              ▼
                                   Prometheus scrapes
                                   metrics every 15s
                                              │
                                              ▼
                                   Grafana shows live
                                   dashboards + alerts
```

---

## 14. Expected Outcomes

1. A working web application accessible through a browser.
2. Source code version-controlled on GitHub with commit history.
3. Automated tests that validate application functionality.
4. A Jenkins pipeline that automates the entire build-test-deploy cycle.
5. A Docker image published to Docker Hub.
6. Automated deployment that only proceeds after tests pass.
7. Real-time monitoring dashboards showing system and application health.
8. Alert rules that detect application downtime.

---

## 15. Limitations

1. **Local deployment only** — not deployed to cloud infrastructure.
2. **Single-node** — no clustering, load balancing, or high availability.
3. **SQLite** — not suitable for concurrent production workloads.
4. **No authentication** — the application has no login system.
5. **Webhook requires tunnel** — GitHub webhooks cannot reach localhost Jenkins without a network tunnel or public IP.
6. **Windows Exporter** — provides Windows-specific metrics, not identical to Linux Node Exporter metrics shown in many tutorials.
7. **No HTTPS** — application runs over plain HTTP for simplicity.

---

## 16. Future Scope

1. Deploy to a cloud platform (AWS EC2, GCP, Azure).
2. Add Kubernetes orchestration for scaling.
3. Implement user authentication with role-based access.
4. Migrate from SQLite to PostgreSQL or MySQL.
5. Add code quality gates (SonarQube, linting).
6. Implement blue-green or canary deployment strategies.
7. Add log aggregation with ELK Stack or Loki.
8. Implement Infrastructure as Code using Terraform.
9. Add security scanning (container vulnerability, dependency audit).
10. Set up multi-branch pipeline with pull request workflows.
