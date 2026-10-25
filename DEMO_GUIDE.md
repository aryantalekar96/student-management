# 🎬 PHASE 13 — Complete End-to-End Demo Guide
# Student Management System — DevOps Mini-Project

## DEMO CHECKLIST — Run in this exact order

---

## ✅ PRE-DEMO SETUP (Do this 5 minutes before presenting)

### Start the monitoring stack:
```powershell
cd student-management
docker-compose up -d prometheus grafana node-exporter
```

### Verify everything is running:
```powershell
docker ps
```
Expected output (all 3 should show "Up"):
```
prometheus    Up  → http://localhost:9090
grafana       Up  → http://localhost:3000
node-exporter Up  → http://localhost:9100
```

---

## 🚀 SUCCESS DEMO — 12 Steps

### STEP 1: Modify the Code
Open `app.py` in any text editor and make a small visible change.
For example, change the home page message or add a comment.

```python
# In app.py, change the index route comment to:
# Updated at: 2024 — triggering the pipeline!
```

### STEP 2: Git Push (triggers the pipeline automatically)
```powershell
cd student-management
git add .
git commit -m "Demo: trigger pipeline - small update"
git push origin main
```

### STEP 3: Jenkins Starts Automatically
- Open browser: http://localhost:8080
- You will see a new build starting in the "student-management" job
- The pipeline view shows all 7 stages starting

### STEP 4: Build Success
- In Jenkins, watch Stage 3 (Build) turn GREEN
- It shows: "App imported successfully"

### STEP 5: Tests Pass
- Watch Stage 4 (Test) turn GREEN
- Console shows: "12 passed in 0.xx seconds"
- THIS IS THE GOLDEN RULE GATE — all green means we proceed!

### STEP 6: Docker Image Built
- Watch Stage 5 (Docker Build) turn GREEN
- Jenkins built a fresh Docker image from the updated code

### STEP 7: Image Pushed to Docker Hub
- Watch Stage 6 (Docker Push) turn GREEN
- Go to: https://hub.docker.com/r/YOURNAME/student-management
- You will see the updated image timestamp

### STEP 8: Container Deployed
- Watch Stage 7 (Deploy) turn GREEN
- Jenkins stopped the old container and started a new one

### STEP 9: Open the Running App
- Open browser: http://localhost:5000
- You see the Student Management System home page
- Try: Add a student → View students → Edit → Delete
- Open: http://localhost:5000/health → shows {"status": "healthy"}

### STEP 10: Grafana Shows Metrics
- Open browser: http://localhost:3000
- Login: admin / admin123
- Go to Dashboards → your dashboard
- You should see: CPU usage, Memory usage, App UP status

### STEP 11: Create CPU Load to Trigger Alert
Run this in a new PowerShell window to stress the CPU:
```powershell
# This runs a CPU stress loop for 5 minutes
1..4 | ForEach-Object {
    Start-Job -ScriptBlock { while($true){[math]::Sqrt(99999)} }
}
Write-Host "CPU stress started - wait 5 minutes for alert to fire"
```

Check Prometheus: http://localhost:9090
Query: `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
You should see CPU% rising.

Stop the stress jobs after demo:
```powershell
Get-Job | Stop-Job; Get-Job | Remove-Job
```

### STEP 12: Show the Alert
- Open Grafana: http://localhost:3000
- Go to Alerting → Alert Rules
- You will see "HighCPUUsage" in "Pending" or "Firing" state
- In Prometheus: http://localhost:9090/alerts
  Shows the alert with its status

---

## ❌ FAILURE DEMO — How the Pipeline Stops

### PURPOSE: Show the Golden Rule — broken tests = NO deployment

### Step 1: Break a test on purpose
Open `test_app.py` and change ONE line to make a test fail:

```python
# Find this line in test_home_page_loads:
assert response.status_code == 200

# Change it to: (this will always FAIL)
assert response.status_code == 999  # INTENTIONALLY BROKEN FOR DEMO
```

### Step 2: Push the broken code
```powershell
git add test_app.py
git commit -m "DEMO: intentionally broken test — should stop pipeline"
git push origin main
```

### Step 3: Watch Jenkins in the browser
- Jenkins starts the pipeline automatically
- Stage 1, 2, 3 pass (green)
- Stage 4 (Test) → turns RED and STOPS
- Stage 5, 6, 7 NEVER run → NO Docker build → NO deployment
- The old working version is still running at localhost:5000

### Step 4: Show the examiner
- The console output shows: "1 failed in 0.xx seconds"
- The pipeline has a red X on Stage 4
- The app is still serving the OLD (working) version

### Step 5: Fix and re-deploy
Change the test back to `== 200`, commit, and push again.
Watch the pipeline go all green.

---

## 📋 QUICK COMMAND REFERENCE

| What | Command |
|---|---|
| Start monitoring stack | `docker-compose up -d` |
| Stop monitoring stack | `docker-compose down` |
| View running containers | `docker ps` |
| View app logs | `docker logs student-app` |
| Run tests manually | `pytest test_app.py -v` |
| Open app | http://localhost:5000 |
| Open Jenkins | http://localhost:8080 |
| Open Prometheus | http://localhost:9090 |
| Open Grafana | http://localhost:3000 (admin/admin123) |

---

## ❓ LIKELY VIVA QUESTIONS — Model Answers

**Q1: What is the purpose of the Jenkinsfile?**
> "The Jenkinsfile defines the entire CI/CD pipeline as code. It is stored in the GitHub repo alongside the application code. Jenkins reads it automatically when code is pushed. This means the pipeline definition is version-controlled, reviewable, and reproducible."

**Q2: What happens if a test fails in Stage 4?**
> "Jenkins marks Stage 4 as failed and immediately stops the pipeline. Stages 5, 6, and 7 — Docker Build, Docker Push, and Deploy — never execute. This enforces the Golden Rule: only tested, verified code gets deployed."

**Q3: What is a Webhook?**
> "A webhook is an automatic HTTP message sent by GitHub to Jenkins the moment a developer pushes code. It acts like a doorbell — GitHub rings Jenkins and says 'new code arrived, start the pipeline.' This makes the pipeline trigger instantly and automatically."

**Q4: What is the difference between a Docker image and a container?**
> "A Docker image is a read-only blueprint — like a recipe or a class in programming. A container is a running instance of that image — like a dish cooked from the recipe, or an object created from the class. One image can create many containers."

**Q5: Why do we push the image to Docker Hub?**
> "Docker Hub is a central registry. Pushing the image there means: (1) it's backed up, (2) any computer can pull and run the same image, (3) different team members or servers can deploy the exact same version. It decouples building from deploying."

**Q6: What does Prometheus scrape?**
> "Prometheus collects metrics by sending HTTP GET requests to each target's /metrics endpoint every 15 seconds. For system metrics, it scrapes Node Exporter at port 9100. For our app, it hits our /health endpoint. All collected data is stored in Prometheus' time-series database."

**Q7: What is the difference between Prometheus and Grafana?**
> "Prometheus collects and stores metrics as numbers. It has a basic UI for querying but no visual dashboards. Grafana connects to Prometheus as a data source and displays those numbers as charts, graphs, and panels with a beautiful UI. Prometheus measures; Grafana visualises."

**Q8: Explain the CPU alert rule.**
> "The alert rule HighCPUUsage uses PromQL to calculate CPU usage: 100 minus the idle CPU percentage. If this value exceeds 80% for more than 5 continuous minutes, the alert fires. The 'for: 5m' prevents false alarms from brief CPU spikes during startup or momentary loads."
