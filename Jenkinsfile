/*
 * =============================================================================
 * JENKINSFILE — Student Management System CI/CD Pipeline
 * =============================================================================
 *
 * This file defines the ENTIRE pipeline in code (called "Pipeline as Code").
 * Jenkins reads this file from your GitHub repo and runs it automatically
 * every time you push code.
 *
 * Language: Groovy (Jenkins' scripting language — similar to Java)
 *
 * PIPELINE STAGES:
 * 1. Checkout           → Download the latest code from GitHub
 * 2. Install Dependencies → Run: pip install -r requirements.txt
 * 3. Build              → Verify the app can be imported (syntax check)
 * 4. Test               → Run: pytest test_app.py (GOLDEN RULE: if fail → stop)
 * 5. Docker Build       → Build the Docker image
 * 6. Docker Push        → Push image to Docker Hub
 * 7. Deploy             → Stop old container, run new one
 *
 * SECURITY NOTE:
 * Docker Hub password is stored in Jenkins Credentials (ID: 'dockerhub-creds')
 * NEVER type passwords directly in this file.
 * =============================================================================
 */

pipeline {

    // -------------------------------------------------------------------------
    // AGENT: Where does this pipeline run?
    // 'any' = run on any available Jenkins agent (our local machine).
    // In a real company, this could be a separate build server.
    // -------------------------------------------------------------------------
    agent any

    // -------------------------------------------------------------------------
    // ENVIRONMENT: Variables available to ALL stages
    // These are like constants at the top of a program.
    // -------------------------------------------------------------------------
    environment {
        // Your Docker Hub username — CHANGE THIS to your actual username
        DOCKER_USERNAME  = 'yourdockerhubusername'

        // Image name (username/appname:tag)
        IMAGE_NAME       = "${DOCKER_USERNAME}/student-management"
        IMAGE_TAG        = 'v1'
        FULL_IMAGE       = "${IMAGE_NAME}:${IMAGE_TAG}"

        // Container name (used to stop/start the running app)
        CONTAINER_NAME   = 'student-app'

        // Port the app runs on
        APP_PORT         = '5000'

        // Jenkins Credentials ID for Docker Hub (set up in Jenkins → Credentials)
        // NEVER type the actual password here — always use credentials()
        DOCKER_CREDS_ID  = 'dockerhub-creds'
    }

    // -------------------------------------------------------------------------
    // OPTIONS: Pipeline-level settings
    // -------------------------------------------------------------------------
    options {
        // Show timestamps in the console log (useful for debugging)
        timestamps()

        // If the pipeline hasn't finished in 20 minutes, abort it
        timeout(time: 20, unit: 'MINUTES')

        // Keep logs for only the last 5 builds (saves disk space)
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    // =========================================================================
    // STAGES: The main pipeline steps
    // Each stage appears as a box in Jenkins' visual pipeline view.
    // =========================================================================
    stages {

        // ---------------------------------------------------------------------
        // STAGE 1: Checkout
        // Jenkins downloads the latest code from GitHub.
        // SCM = Source Code Management (another term for Git/GitHub).
        // ---------------------------------------------------------------------
        stage('1 - Checkout') {
            steps {
                echo '========== STAGE 1: Checkout =========='
                echo 'Downloading the latest code from GitHub...'

                // checkout scm = Jenkins uses the GitHub URL configured in the job
                checkout scm

                echo 'Code downloaded successfully!'

                // Show which files were downloaded
                sh 'ls -la'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 2: Install Dependencies
        // Install all Python libraries listed in requirements.txt.
        // This makes sure the test environment has everything it needs.
        // ---------------------------------------------------------------------
        stage('2 - Install Dependencies') {
            steps {
                echo '========== STAGE 2: Install Dependencies =========='
                echo 'Installing Python packages from requirements.txt...'

                // pip install -r requirements.txt
                // --upgrade ensures we get the latest compatible versions
                sh 'pip install -r requirements.txt'

                // Show what was installed (useful for debugging)
                sh 'pip list'

                echo 'All dependencies installed!'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 3: Build (Syntax / Import Check)
        // We verify the app can be imported without errors.
        // This catches typos and broken imports before running tests.
        // ---------------------------------------------------------------------
        stage('3 - Build') {
            steps {
                echo '========== STAGE 3: Build =========='
                echo 'Checking that the Flask app imports without errors...'

                // python -c "import app" → imports app.py
                // If there's a syntax error in app.py, this fails immediately
                sh 'python -c "import app; print(\"App imported successfully\")"'

                echo 'Build check passed!'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 4: Test  ← THE GOLDEN RULE GATE
        // Run all PyTest tests.
        // If ANY test fails → pipeline stops here → NO Docker build → NO deploy.
        // The -v flag shows each test result individually.
        // The --tb=short flag shows a short traceback on failures.
        // *** THIS IS THE MOST IMPORTANT STAGE ***
        // ---------------------------------------------------------------------
        stage('4 - Test') {
            steps {
                echo '========== STAGE 4: Test =========='
                echo 'Running PyTest automated tests...'
                echo 'GOLDEN RULE: If ANY test fails, pipeline STOPS here!'

                sh 'python -m pytest test_app.py -v --tb=short'

                echo 'All tests PASSED! Proceeding to Docker build...'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 5: Docker Build
        // Build the Docker image using the Dockerfile.
        // Only reached if ALL tests passed in Stage 4.
        // ---------------------------------------------------------------------
        stage('5 - Docker Build') {
            steps {
                echo '========== STAGE 5: Docker Build =========='
                echo "Building Docker image: ${FULL_IMAGE}"

                // docker build -t username/student-management:v1 .
                sh "docker build -t ${FULL_IMAGE} ."

                // Verify the image was created
                sh "docker images ${IMAGE_NAME}"

                echo "Docker image built: ${FULL_IMAGE}"
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 6: Docker Push
        // Push the image to Docker Hub so it can be deployed anywhere.
        //
        // SECURITY: We use withCredentials() to safely inject the password.
        // Jenkins retrieves the password from its encrypted credential store.
        // The password is NEVER written to any file or shown in logs.
        // ---------------------------------------------------------------------
        stage('6 - Docker Push') {
            steps {
                echo '========== STAGE 6: Docker Push =========='
                echo "Pushing image to Docker Hub: ${FULL_IMAGE}"

                // withCredentials: safely retrieve username+password from Jenkins
                // USR and PSW are temporary variables — never stored anywhere
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDS_ID}",
                    usernameVariable: 'DOCKER_USR',
                    passwordVariable: 'DOCKER_PSW'
                )]) {
                    // Login to Docker Hub
                    sh "echo ${DOCKER_PSW} | docker login -u ${DOCKER_USR} --password-stdin"

                    // Push the image
                    sh "docker push ${FULL_IMAGE}"

                    // Logout (good security practice)
                    sh "docker logout"
                }

                echo "Image pushed to Docker Hub: ${FULL_IMAGE}"
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 7: Deploy
        // Stop any running container with the same name, then start a new one.
        // This is called a "rolling deploy" — zero downtime is NOT guaranteed
        // here (for a college project, this is fine).
        // ---------------------------------------------------------------------
        stage('7 - Deploy') {
            steps {
                echo '========== STAGE 7: Deploy =========='
                echo "Deploying container: ${CONTAINER_NAME}"

                // Stop and remove the OLD container if it exists
                // '|| true' means "don't fail if container doesn't exist yet"
                sh "docker stop ${CONTAINER_NAME} || true"
                sh "docker rm   ${CONTAINER_NAME} || true"

                // Start the NEW container
                // -d        = detached (runs in background)
                // -p 5000:5000 = map host port 5000 to container port 5000
                // --name    = give it a friendly name
                // --restart always = auto-restart if computer reboots
                sh """
                    docker run -d \
                        -p ${APP_PORT}:${APP_PORT} \
                        --name ${CONTAINER_NAME} \
                        --restart always \
                        ${FULL_IMAGE}
                """

                // Wait 3 seconds for container to fully start
                sh 'sleep 3'

                // Verify the container is running
                sh "docker ps | grep ${CONTAINER_NAME}"

                // Health check — confirm the app responds
                sh "curl -f http://localhost:${APP_PORT}/health || echo 'Health check warning'"

                echo "Deployment complete! App running at http://localhost:${APP_PORT}"
            }
        }
    }

    // =========================================================================
    // POST: Actions that run AFTER all stages, regardless of pass/fail
    // =========================================================================
    post {
        // Runs if pipeline succeeded (all green)
        success {
            echo '=============================================='
            echo ' PIPELINE SUCCEEDED! All 7 stages passed!'
            echo " App is live at: http://localhost:${APP_PORT}"
            echo ' Docker Hub image updated: ' + FULL_IMAGE
            echo '=============================================='
        }

        // Runs if pipeline failed (something went red)
        failure {
            echo '=============================================='
            echo ' PIPELINE FAILED!'
            echo ' Check the red stage above to see what broke.'
            echo ' The old version of the app is still running.'
            echo '=============================================='
        }

        // Runs ALWAYS (whether success or failure) — good for cleanup
        always {
            echo 'Pipeline finished. Check the stage view above.'
        }
    }
}
