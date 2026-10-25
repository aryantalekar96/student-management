/*
 * =============================================================================
 * JENKINSFILE — Student Management System CI/CD Pipeline
 * =============================================================================
 *
 * WINDOWS VERSION — uses 'bat' instead of 'sh'
 *
 * WHY bat NOT sh?
 *   sh  = Linux/Mac shell command  (bash)
 *   bat = Windows shell command    (cmd.exe)
 *   Jenkins on Windows cannot run 'sh' — it throws "cannot find file sh"
 *   So every shell command must use 'bat' on Windows.
 *
 * PIPELINE STAGES:
 * 1. Checkout           → Download the latest code from GitHub
 * 2. Install Dependencies → pip install -r requirements.txt
 * 3. Build              → Verify app.py imports without errors
 * 4. Test               → pytest test_app.py (GOLDEN RULE gate)
 * 5. Docker Build       → docker build
 * 6. Docker Push        → docker push to Docker Hub
 * 7. Deploy             → stop old container, start new one
 *
 * SECURITY: Docker Hub password stored in Jenkins Credentials
 * ID: 'dockerhub-creds' — never typed in plain text here.
 * =============================================================================
 */

pipeline {

    // -------------------------------------------------------------------------
    // AGENT: Run on any available machine (our Windows laptop)
    // -------------------------------------------------------------------------
    agent any

    // -------------------------------------------------------------------------
    // ENVIRONMENT: Variables shared across all stages
    // -------------------------------------------------------------------------
    environment {
        DOCKER_USERNAME  = 'aryantalekar96'
        IMAGE_NAME       = "${DOCKER_USERNAME}/student-management"
        IMAGE_TAG        = 'v1'
        FULL_IMAGE       = "${IMAGE_NAME}:${IMAGE_TAG}"
        CONTAINER_NAME   = 'student-app'
        APP_PORT         = '5000'
        DOCKER_CREDS_ID  = 'dockerhub-creds'
    }

    // -------------------------------------------------------------------------
    // OPTIONS: Pipeline settings
    // -------------------------------------------------------------------------
    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    // =========================================================================
    // STAGES
    // =========================================================================
    stages {

        // ---------------------------------------------------------------------
        // STAGE 1: Checkout
        // Downloads latest code from GitHub into Jenkins workspace.
        // 'checkout scm' uses the GitHub URL configured in the Jenkins job.
        // ---------------------------------------------------------------------
        stage('1 - Checkout') {
            steps {
                echo '========== STAGE 1: Checkout =========='
                echo 'Downloading the latest code from GitHub...'

                checkout scm

                echo 'Code downloaded successfully!'

                // 'bat dir' = Windows equivalent of 'ls -la' on Linux
                // Shows all files in the Jenkins workspace folder
                bat 'dir'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 2: Install Dependencies
        // Installs all Python packages listed in requirements.txt.
        // Jenkins workspace is a clean folder — we must install every time.
        // ---------------------------------------------------------------------
        stage('2 - Install Dependencies') {
            steps {
                echo '========== STAGE 2: Install Dependencies =========='
                echo 'Installing Python packages from requirements.txt...'

                // pip install reads requirements.txt and installs flask, pytest, requests
                bat 'pip install -r requirements.txt'

                // Show installed packages — useful for debugging version issues
                bat 'pip list'

                echo 'All dependencies installed!'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 3: Build
        // Imports app.py to check for syntax errors.
        // If app.py has a typo or broken import, this stage fails immediately.
        // This is faster than waiting for tests to discover the same problem.
        // ---------------------------------------------------------------------
        stage('3 - Build') {
            steps {
                echo '========== STAGE 3: Build =========='
                echo 'Checking that the Flask app imports without errors...'

                // python -c runs a single Python statement
                // If app.py has ANY syntax error, this throws an exception
                bat 'python -c "import app; print(\'App imported successfully\')"'

                echo 'Build check passed!'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 4: Test  ←  THE GOLDEN RULE GATE
        //
        // THIS IS THE MOST IMPORTANT STAGE.
        // If ANY test fails here:
        //   → Jenkins marks this stage RED
        //   → Stages 5, 6, 7 are ALL skipped
        //   → No Docker image is built
        //   → No deployment happens
        //   → The old working version keeps running
        //
        // This enforces the Golden Rule:
        //   "Only tested, verified code gets deployed."
        // ---------------------------------------------------------------------
        stage('4 - Test') {
            steps {
                echo '========== STAGE 4: Test =========='
                echo 'Running PyTest automated tests...'
                echo 'GOLDEN RULE: If ANY test fails, pipeline STOPS here!'

                // -v        = verbose (show each test name)
                // --tb=short = short error message on failure
                bat 'python -m pytest test_app.py -v --tb=short'

                echo 'All tests PASSED! Proceeding to Docker build...'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 5: Docker Build
        // Builds a Docker image from our Dockerfile.
        // Only runs if ALL tests in Stage 4 passed.
        // The image contains: Python + Flask + our app code, all in one box.
        // ---------------------------------------------------------------------
        stage('5 - Docker Build') {
            steps {
                echo '========== STAGE 5: Docker Build =========='
                echo "Building Docker image: ${FULL_IMAGE}"

                // Build the image and tag it with username/appname:version
                bat "docker build -t ${FULL_IMAGE} ."

                // List images to confirm it was created
                bat "docker images ${IMAGE_NAME}"

                echo "Docker image built: ${FULL_IMAGE}"
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 6: Docker Push
        // Pushes the image to Docker Hub.
        //
        // SECURITY — withCredentials():
        //   Jenkins retrieves username+password from its encrypted vault.
        //   The password is injected as an environment variable (DOCKER_PSW).
        //   It is NEVER written to disk or shown in logs (masked as ****).
        // ---------------------------------------------------------------------
        stage('6 - Docker Push') {
            steps {
                echo '========== STAGE 6: Docker Push =========='
                echo "Pushing image to Docker Hub: ${FULL_IMAGE}"

                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDS_ID}",
                    usernameVariable: 'DOCKER_USR',
                    passwordVariable: 'DOCKER_PSW'
                )]) {
                    bat 'echo %DOCKER_PSW%| docker login -u %DOCKER_USR% --password-stdin'
                    bat "docker push ${FULL_IMAGE}"
                    bat "docker logout"
                }

                echo "Image pushed to Docker Hub: ${FULL_IMAGE}"
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 7: Deploy
        // Stops the old container and starts a fresh one from the new image.
        // This is the "Continuous Deployment" part of CI/CD.
        //
        // || exit 0 = Windows equivalent of Linux's '|| true'
        // It means: "if this command fails, don't stop the pipeline"
        // Used for stop/rm because the container may not exist on first run.
        // ---------------------------------------------------------------------
        stage('7 - Deploy') {
            steps {
                echo '========== STAGE 7: Deploy =========='
                echo "Deploying container: ${CONTAINER_NAME}"

                // Stop old container — || exit 0 prevents failure if not running
                bat "docker stop ${CONTAINER_NAME} || exit 0"
                bat "docker rm   ${CONTAINER_NAME} || exit 0"

                // Start new container
                // -d             = run in background (detached)
                // -p 5000:5000   = expose port 5000 to the host
                // --name         = give it a memorable name
                // --restart always = auto-restart if machine reboots
                bat "docker run -d -p ${APP_PORT}:${APP_PORT} --name ${CONTAINER_NAME} --restart always ${FULL_IMAGE}"

                // Wait 3 seconds for the container to fully start
                bat 'timeout /t 3 /nobreak > nul'

                // Verify container is running — 'findstr' is Windows grep
                bat "docker ps | findstr ${CONTAINER_NAME}"

                echo "Deployment complete! App running at http://localhost:${APP_PORT}"
            }
        }
    }

    // =========================================================================
    // POST: Runs after all stages finish (pass or fail)
    // =========================================================================
    post {
        success {
            echo '=============================================='
            echo ' PIPELINE SUCCEEDED! All 7 stages passed!'
            echo " App is live at: http://localhost:${APP_PORT}"
            echo " Docker Hub:     ${FULL_IMAGE}"
            echo '=============================================='
        }
        failure {
            echo '=============================================='
            echo ' PIPELINE FAILED!'
            echo ' Check the red stage above to see what broke.'
            echo ' The previous version of the app is still running.'
            echo '=============================================='
        }
        always {
            echo 'Pipeline finished. Check the stage view above.'
        }
    }
}
