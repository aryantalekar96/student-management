/*
 * Jenkinsfile — Declarative Pipeline for Student Management System
 *
 * BEGINNER EXPLANATION:
 * ─────────────────────
 * A Jenkinsfile tells Jenkins exactly how to build, test, and deploy
 * your application automatically every time code is pushed to GitHub.
 *
 * Key concepts:
 *   pipeline  → the entire automated workflow
 *   agent     → where Jenkins runs the pipeline (any available machine)
 *   stages    → the big steps (Checkout, Test, Build, Deploy…)
 *   stage     → one single step
 *   steps     → the actual commands inside each stage
 *   environment → variables available to all stages
 *   post      → actions that run AFTER the pipeline (success/failure)
 *
 * Pipeline flow:
 *   Code Push → GitHub Webhook → Jenkins → [Pipeline Below] → Deployment
 */

pipeline {

    // Run on any available Jenkins agent (worker machine)
    agent any

    // ─── Environment Variables ────────────────────────────────────────────
    // These are available to every stage. ${BUILD_NUMBER} is set by Jenkins
    // automatically — it increments with each build (1, 2, 3, …)
    environment {
        // Docker Hub username — CHANGE THIS to your Docker Hub username
        DOCKER_HUB_USER  = "aryantalekar96"
        IMAGE_NAME       = "student-management"
        IMAGE_TAG        = "${BUILD_NUMBER}"
        FULL_IMAGE       = "${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE     = "${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"

        // Container settings for deployment
        CONTAINER_NAME   = "student-management-app"
        APP_PORT         = "5001"          // host port (maps to 5000 in container)
        DATA_VOLUME      = "student-data"  // Docker named volume for SQLite

        // Jenkins credential ID for Docker Hub (set up in Jenkins → Credentials)
        DOCKER_CREDENTIALS_ID = "dockerhub-credentials"
    }

    options {
        // Keep only the last 10 builds to save disk space
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Fail if the pipeline takes more than 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        // Add timestamps to all log output
        timestamps()
    }

    // ─── Pipeline Stages ─────────────────────────────────────────────────

    stages {

        // ── Stage 1: Checkout ──────────────────────────────────────────
        // Jenkins checks out (downloads) the source code from GitHub.
        // This is always the first stage.
        stage('Checkout') {
            steps {
                echo '━━━ Stage 1: Checking out source code from GitHub ━━━'
                // 'checkout scm' automatically uses the repository configured
                // in the Jenkins job — it knows the URL and branch to pull
                checkout scm
                sh 'echo "Current directory: $(pwd)"'
                sh 'echo "Files checked out:"; ls -la'
                sh 'git log --oneline -5'
            }
        }

        // ── Stage 2: Install Dependencies ─────────────────────────────
        // Creates a Python virtual environment and installs all packages
        // listed in requirements.txt
        stage('Install Dependencies') {
            steps {
                echo '━━━ Stage 2: Installing Python dependencies ━━━'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "Installed packages:"
                    pip list
                '''
            }
        }

        // ── Stage 3: Run Automated Tests ──────────────────────────────
        // Run ALL pytest tests. If ANY test fails → pipeline stops here.
        // We NEVER deploy untested code. This is the core CI principle.
        stage('Test') {
            steps {
                echo '━━━ Stage 3: Running automated tests with pytest ━━━'
                sh '''
                    . venv/bin/activate
                    python -m pytest test_app.py -v \
                        --tb=short \
                        --junit-xml=test-results.xml
                    echo "Test run complete."
                '''
            }
            post {
                // Always publish test results to Jenkins, even on failure
                always {
                    junit 'test-results.xml'
                }
                failure {
                    echo '✗ Tests FAILED — stopping pipeline. No deployment will occur.'
                }
                success {
                    echo '✓ All tests passed — proceeding to Docker build.'
                }
            }
        }

        // ── Stage 4: Build Docker Image ───────────────────────────────
        // Builds the Docker image using the Dockerfile in the repository.
        // Tags it with both the build number AND 'latest'.
        stage('Docker Build') {
            steps {
                echo "━━━ Stage 4: Building Docker image: ${FULL_IMAGE} ━━━"
                sh """
                    docker build \
                        --tag ${FULL_IMAGE} \
                        --tag ${LATEST_IMAGE} \
                        --label "build-number=${BUILD_NUMBER}" \
                        --label "git-commit=${GIT_COMMIT}" \
                        .
                    echo "Image built successfully."
                    docker images | grep ${IMAGE_NAME}
                """
            }
        }

        // ── Stage 5: Push to Docker Hub ───────────────────────────────
        // Logs in to Docker Hub using stored credentials (never hardcoded!)
        // and pushes both the versioned tag and the 'latest' tag.
        stage('Docker Push') {
            steps {
                echo "━━━ Stage 5: Pushing image to Docker Hub ━━━"
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDENTIALS_ID}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        docker push ${FULL_IMAGE}
                        docker push ${LATEST_IMAGE}
                        echo "Image pushed: ${FULL_IMAGE}"
                        docker logout
                    """
                }
            }
        }

        // ── Stage 6: Deploy ───────────────────────────────────────────
        // Stops any existing container, creates a data volume (if needed),
        // and starts a fresh container from the newly pushed image.
        stage('Deploy') {
            steps {
                echo "━━━ Stage 6: Deploying container ━━━"
                sh """
                    # Create a named volume for database persistence (if it doesn't exist)
                    docker volume create ${DATA_VOLUME} || true

                    # Stop and remove the old container (if running)
                    docker stop ${CONTAINER_NAME} || true
                    docker rm   ${CONTAINER_NAME} || true

                    # Start the new container
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p ${APP_PORT}:5000 \
                        -v ${DATA_VOLUME}:/app/data \
                        ${LATEST_IMAGE}

                    echo "Container started. Waiting 5 seconds for startup..."
                    sleep 5

                    # Verify the container is running
                    docker ps | grep ${CONTAINER_NAME}

                    # Health check
                    curl -f http://localhost:${APP_PORT}/health || \
                        (echo "Health check FAILED" && exit 1)

                    echo "✓ Deployment successful! App running at http://localhost:${APP_PORT}"
                """
            }
        }

    } // end stages

    // ─── Post-Pipeline Actions ────────────────────────────────────────────
    post {
        success {
            echo """
            ╔══════════════════════════════════════════════════╗
            ║  ✓ PIPELINE SUCCESSFUL — Build #${BUILD_NUMBER}  ║
            ║  Image: ${FULL_IMAGE}                            ║
            ║  App URL: http://localhost:${APP_PORT}           ║
            ╚══════════════════════════════════════════════════╝
            """
        }
        failure {
            echo """
            ╔══════════════════════════════════════════════════╗
            ║  ✗ PIPELINE FAILED — Build #${BUILD_NUMBER}      ║
            ║  Check the logs above for the failing stage.     ║
            ╚══════════════════════════════════════════════════╝
            """
        }
        always {
            // Clean up the virtual environment to save disk space
            sh 'rm -rf venv || true'
            echo 'Pipeline finished.'
        }
    }

} // end pipeline
