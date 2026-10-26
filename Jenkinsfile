/*
 * =============================================================================
 * JENKINSFILE — Student Management System CI/CD Pipeline
 * =============================================================================
 *
 * WINDOWS VERSION — uses 'bat' instead of 'sh'
 *
 * WHY bat NOT sh?
 *   sh  = Linux/Mac shell  (not available on Windows Jenkins)
 *   bat = Windows cmd.exe  (correct for Windows)
 *
 * PIPELINE STAGES:
 * 1. Checkout           → Download latest code from GitHub
 * 2. Install Dependencies → pip install -r requirements.txt
 * 3. Build              → Verify app.py imports without errors
 * 4. Test               → pytest test_app.py  ← GOLDEN RULE GATE
 * 5. Docker Build       → docker build
 * 6. Docker Push        → docker push to Docker Hub
 * 7. Deploy             → stop old container, start new one on monitoring network
 *
 * SECURITY: Docker Hub password stored in Jenkins Credentials ID: 'dockerhub-creds'
 * =============================================================================
 */

pipeline {

    agent any

    environment {
        DOCKER_USERNAME  = 'aryantalekar96'
        IMAGE_NAME       = "${DOCKER_USERNAME}/student-management"
        IMAGE_TAG        = 'v1'
        FULL_IMAGE       = "${IMAGE_NAME}:${IMAGE_TAG}"
        CONTAINER_NAME   = 'student-app'
        APP_PORT         = '5000'
        DOCKER_CREDS_ID  = 'dockerhub-creds'
    }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    stages {

        // ---------------------------------------------------------------------
        // STAGE 1: Checkout
        // Downloads latest code from GitHub into Jenkins workspace.
        // checkout scm uses the GitHub URL configured in the Jenkins job.
        // bat 'dir' = Windows equivalent of Linux 'ls -la'
        // ---------------------------------------------------------------------
        stage('1 - Checkout') {
            steps {
                echo '========== STAGE 1: Checkout =========='
                echo 'Downloading the latest code from GitHub...'
                checkout scm
                echo 'Code downloaded successfully!'
                bat 'dir'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 2: Install Dependencies
        // Installs all Python packages from requirements.txt.
        // ---------------------------------------------------------------------
        stage('2 - Install Dependencies') {
            steps {
                echo '========== STAGE 2: Install Dependencies =========='
                echo 'Installing Python packages from requirements.txt...'
                bat 'pip install -r requirements.txt'
                bat 'pip list'
                echo 'All dependencies installed!'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 3: Build
        // Imports app.py to verify no syntax errors exist.
        // Fails immediately if app.py has any broken code.
        // ---------------------------------------------------------------------
        stage('3 - Build') {
            steps {
                echo '========== STAGE 3: Build =========='
                echo 'Checking that the Flask app imports without errors...'
                bat 'python -c "import app; print(\'App imported successfully\')"'
                echo 'Build check passed!'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 4: Test  ← THE GOLDEN RULE GATE
        //
        // If ANY test fails:
        //   → This stage turns RED
        //   → Stages 5, 6, 7 are ALL skipped
        //   → No Docker image built, no deployment
        //   → Old working version keeps running
        //
        // This enforces: "Only tested code gets deployed."
        // ---------------------------------------------------------------------
        stage('4 - Test') {
            steps {
                echo '========== STAGE 4: Test =========='
                echo 'Running PyTest automated tests...'
                echo 'GOLDEN RULE: If ANY test fails, pipeline STOPS here!'
                bat 'python -m pytest test_app.py -v --tb=short'
                echo 'All tests PASSED! Proceeding to Docker build...'
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 5: Docker Build
        // Builds Docker image from Dockerfile.
        // Only runs if ALL tests in Stage 4 passed.
        // ---------------------------------------------------------------------
        stage('5 - Docker Build') {
            steps {
                echo '========== STAGE 5: Docker Build =========='
                echo "Building Docker image: ${FULL_IMAGE}"
                bat "docker build -t ${FULL_IMAGE} ."
                bat "docker images ${IMAGE_NAME}"
                echo "Docker image built: ${FULL_IMAGE}"
            }
        }

        // ---------------------------------------------------------------------
        // STAGE 6: Docker Push
        // Pushes image to Docker Hub using credentials stored securely in Jenkins.
        //
        // withCredentials: retrieves username+password from Jenkins vault.
        // The password is NEVER shown in logs (masked as ****).
        //
        // NOTE: No space before pipe (echo %DOCKER_PSW%|) — space causes
        // Windows to include it in the password, causing auth failure.
        // Single quotes prevent Groovy from interpreting %VAR% before cmd does.
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
        // Stops old container, starts fresh one from the new image.
        //
        // --network student-management_monitoring-network:
        //   Puts the container on the same Docker network as Prometheus.
        //   This means Prometheus can reach the app at student-app:5000
        //   automatically — no manual 'docker network connect' needed.
        //
        // sleep(time:3): Jenkins built-in — works on all OS.
        //   Replaces 'timeout /t 3' which is Windows-only and can fail in Jenkins.
        //
        // || exit 0: Windows equivalent of Linux '|| true'
        //   Prevents pipeline failure if container doesn't exist yet (first run).
        // ---------------------------------------------------------------------
        stage('7 - Deploy') {
            steps {
                echo '========== STAGE 7: Deploy =========='
                echo "Deploying container: ${CONTAINER_NAME}"

                bat "docker stop ${CONTAINER_NAME} || exit 0"
                bat "docker rm   ${CONTAINER_NAME} || exit 0"

                bat "docker run -d -p ${APP_PORT}:${APP_PORT} --name ${CONTAINER_NAME} --network student-management_monitoring-network --restart always ${FULL_IMAGE}"

                sleep(time: 3, unit: 'SECONDS')

                bat "docker ps | findstr ${CONTAINER_NAME}"

                echo "Deployment complete! App running at http://localhost:${APP_PORT}"
            }
        }
    }

    post {
        success {
            echo '=============================================='
            echo ' PIPELINE SUCCEEDED! All 7 stages passed!'
            echo " App        : http://localhost:${APP_PORT}"
            echo " Docker Hub : https://hub.docker.com/r/${DOCKER_USERNAME}/student-management"
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
