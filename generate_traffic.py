"""
Traffic Generator for Student Management System
Generates diverse HTTP traffic (GET, POST, 200 OK, 302 Redirect, 404 Not Found)
to demonstrate live metrics in Prometheus & Grafana.
"""

import time
import random
import urllib.request
import urllib.parse
import urllib.error

import os

BASE_URL = os.environ.get("APP_URL", "http://localhost:5001")

SAMPLE_STUDENTS = [
    ("Aarav Sharma", "aarav@example.com", "Computer Science"),
    ("Diya Patel", "diya@example.com", "Information Technology"),
    ("Rohan Mehta", "rohan@example.com", "Data Science"),
    ("Ananya Iyer", "ananya@example.com", "Artificial Intelligence"),
    ("Vikram Singh", "vikram@example.com", "Cyber Security"),
    ("Sneha Kulkarni", "sneha@example.com", "Mechanical Engineering"),
]

def send_request(method, path, data=None):
    url = f"{BASE_URL}{path}"
    try:
        encoded_data = None
        if data:
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data, method=method)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR ({e})"

def run_traffic_loop(rounds=50, delay=0.4):
    print("=" * 65)
    print("  [*] Starting Traffic Generator for Student Management System")
    print(f"  Target: {BASE_URL}")
    print(f"  Rounds: {rounds} iterations | Delay: {delay}s")
    print("=" * 65)

    stats = {"200": 0, "302": 0, "404": 0, "other": 0}

    for i in range(1, rounds + 1):
        action = random.choice([
            "home", "list", "health", "add_student", "metrics",
            "not_found", "validation_fail"
        ])

        if action == "home":
            status = send_request("GET", "/")
            desc = "GET  / (Home)"
        elif action == "list":
            status = send_request("GET", "/students")
            desc = "GET  /students"
        elif action == "health":
            status = send_request("GET", "/health")
            desc = "GET  /health"
        elif action == "metrics":
            status = send_request("GET", "/metrics")
            desc = "GET  /metrics"
        elif action == "add_student":
            name, email, course = random.choice(SAMPLE_STUDENTS)
            # Add random suffix to make email unique
            email = f"{random.randint(100, 999)}_{email}"
            status = send_request("POST", "/add", {
                "name": name,
                "email": email,
                "course": course
            })
            desc = f"POST /add ({name})"
        elif action == "validation_fail":
            status = send_request("POST", "/add", {
                "name": "",
                "email": "invalid-email",
                "course": ""
            })
            desc = "POST /add (Validation Error)"
        elif action == "not_found":
            status = send_request("GET", f"/nonexistent-{random.randint(1, 100)}")
            desc = "GET  /nonexistent (404 Test)"

        key = str(status)
        if key in stats:
            stats[key] += 1
        else:
            stats["other"] += 1

        print(f"[{i:03d}/{rounds:03d}] {desc:<35} -> HTTP {status}")
        time.sleep(delay)

    print("=" * 65)
    print(f"  [+] Traffic simulation complete! Summary: {stats}")
    print("  Check Grafana at: http://localhost:3000")
    print("  Check Prometheus at: http://localhost:9090")
    print("=" * 65)

if __name__ == "__main__":
    import sys
    count = 100 if len(sys.argv) < 2 else int(sys.argv[1])
    run_traffic_loop(rounds=count)
