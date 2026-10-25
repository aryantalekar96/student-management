# JENKINS_SETUP.md
# =================
# Step-by-step guide to configure Jenkins for this project.
# Do this ONCE after Jenkins is installed.

---

## STEP 1: Download and Start Jenkins

If not already running:
```powershell
# Download jenkins.war from https://www.jenkins.io/download/ (Generic Java package)
# Then run:
java -jar jenkins.war --httpPort=8080
```

Open: http://localhost:8080

---

## STEP 2: Unlock Jenkins (First Time Only)

Get the initial admin password:
```powershell
type C:\Users\YOUR_USERNAME\.jenkins\secrets\initialAdminPassword
```

Paste it in the browser → Click "Install suggested plugins" → Wait → Create admin user.

---

## STEP 3: Add Docker Hub Credentials (SECURITY — never type passwords in code)

1. Go to: Jenkins → Manage Jenkins → Credentials → System → Global credentials
2. Click: "Add Credentials"
3. Fill in:
   - Kind: Username with password
   - Username: YOUR_DOCKERHUB_USERNAME
   - Password: YOUR_DOCKERHUB_PASSWORD
   - ID: dockerhub-creds    ← IMPORTANT: must match Jenkinsfile exactly
   - Description: Docker Hub credentials
4. Click Save

⚠️ The ID "dockerhub-creds" must match the DOCKER_CREDS_ID in the Jenkinsfile.

---

## STEP 4: Create the Pipeline Job

1. Click: New Item
2. Name: student-management
3. Type: Pipeline
4. Click OK

In the configuration page:

**General:**
- ✅ Check "GitHub project"
- URL: https://github.com/YOUR_USERNAME/student-management

**Build Triggers:**
- ✅ Check "GitHub hook trigger for GITScm polling"
  (This makes Jenkins listen for webhook from GitHub)

**Pipeline:**
- Definition: "Pipeline script from SCM"
- SCM: Git
- Repository URL: https://github.com/YOUR_USERNAME/student-management.git
- Branch: */main
- Script Path: Jenkinsfile

Click Save.

---

## STEP 5: Set Up GitHub Webhook

1. Go to your GitHub repo → Settings → Webhooks → Add webhook
2. Fill in:
   - Payload URL: http://YOUR_IP:8080/github-webhook/
   - Content type: application/json
   - Events: Just the push event
3. Click Add webhook

To find YOUR_IP on Windows:
```powershell
ipconfig | findstr "IPv4"
```

⚠️ If Jenkins is behind a firewall/NAT, GitHub cannot reach localhost:8080 directly.
Solution: Use ngrok to expose localhost:
```powershell
# Download ngrok from https://ngrok.com
ngrok http 8080
# Copy the https URL (e.g. https://abc123.ngrok.io)
# Use that as webhook URL: https://abc123.ngrok.io/github-webhook/
```

---

## STEP 6: Update the Jenkinsfile with Your Docker Hub Username

Open student-management/Jenkinsfile and change this line:
```groovy
DOCKER_USERNAME = 'yourdockerhubusername'
```
Change to your actual Docker Hub username, then commit and push:
```powershell
git add Jenkinsfile
git commit -m "Update Jenkinsfile with correct Docker Hub username"
git push origin main
```

---

## STEP 7: Test the Pipeline

1. In Jenkins, click on "student-management" job
2. Click "Build Now"
3. Watch the pipeline stages run
4. All 7 stages should be green

Then test the webhook:
- Make any small change to app.py
- git add, commit, push
- Jenkins should start automatically within 30 seconds

---

## COMMON ERRORS IN JENKINS

### Error: "docker: command not found"
Fix: Jenkins needs to know where Docker is.
Go to: Manage Jenkins → Global Tool Configuration → Docker
Or add the Docker executable path to the Jenkins PATH.

### Error: "Permission denied" when running Docker
Fix: On Linux, add Jenkins user to docker group:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```
On Windows, run Jenkins as Administrator.

### Error: "Credentials not found: dockerhub-creds"
Fix: The credential ID in Jenkins must exactly match "dockerhub-creds".
Go to: Credentials → check the ID spelling.
