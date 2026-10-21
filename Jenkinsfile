/*
 * Jenkinsfile — Declarative Pipeline for Student Management System
 *
 * Designed to work seamlessly on both Windows and Linux Jenkins environments!
 */

pipeline {

    // Run on any available Jenkins agent (worker machine)
    agent any

    // ─── Environment Variables ────────────────────────────────────────────
    environment {
        // Ensure standard Windows tools are in PATH if running on Windows
        PATH             = "C:\\Users\\Admin\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin;C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python314;C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python314\\Scripts;${env.PATH}"

        // Docker Hub repository settings
        DOCKER_HUB_USER  = "aryantalekar96"
        IMAGE_NAME       = "student-management"
        IMAGE_TAG        = "${BUILD_NUMBER}"
        FULL_IMAGE       = "${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE     = "${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"

        // Container settings for deployment
        CONTAINER_NAME   = "student-management-app"
        APP_PORT         = "5001"          // host port (maps to 5000 in container)
        DATA_VOLUME      = "student-data"  // Docker named volume for SQLite

        // Jenkins credential ID for Docker Hub
        DOCKER_CREDENTIALS_ID = "dockerhub-credentials"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    // ─── Pipeline Stages ─────────────────────────────────────────────────
    stages {

        // ── Stage 1: Checkout ──────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '━━━ Stage 1: Checking out source code from GitHub ━━━'
                checkout scm
                script {
                    if (isUnix()) {
                        sh 'git log --oneline -3'
                    } else {
                        bat 'git log --oneline -3'
                    }
                }
            }
        }

        // ── Stage 2: Install Dependencies ─────────────────────────────
        stage('Install Dependencies') {
            steps {
                echo '━━━ Stage 2: Installing Python dependencies ━━━'
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            python -m pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        // ── Stage 3: Run Automated Tests ──────────────────────────────
        stage('Test') {
            steps {
                echo '━━━ Stage 3: Running automated tests with pytest ━━━'
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            python -m pytest test_app.py -v --tb=short --junit-xml=test-results.xml
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            python -m pytest test_app.py -v --tb=short --junit-xml=test-results.xml
                        '''
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
                failure {
                    echo '✗ Tests FAILED — stopping pipeline.'
                }
                success {
                    echo '✓ All tests passed — proceeding to Docker build.'
                }
            }
        }

        // ── Stage 4: Build Docker Image ───────────────────────────────
        stage('Docker Build') {
            steps {
                echo "━━━ Stage 4: Building Docker image: ${FULL_IMAGE} ━━━"
                script {
                    if (isUnix()) {
                        sh """
                            docker build --tag ${FULL_IMAGE} --tag ${LATEST_IMAGE} .
                            docker images | grep ${IMAGE_NAME}
                        """
                    } else {
                        bat """
                            docker build --tag ${FULL_IMAGE} --tag ${LATEST_IMAGE} .
                            docker images | findstr ${IMAGE_NAME}
                        """
                    }
                }
            }
        }

        // ── Stage 5: Push to Docker Hub ───────────────────────────────
        stage('Docker Push') {
            steps {
                echo "━━━ Stage 5: Pushing image to Docker Hub ━━━"
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    withCredentials([usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS_ID}",
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        script {
                            if (isUnix()) {
                                sh """
                                    echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                                    docker push ${FULL_IMAGE}
                                    docker push ${LATEST_IMAGE}
                                    docker logout
                                """
                            } else {
                                bat """
                                    echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                                    docker push ${FULL_IMAGE}
                                    docker push ${LATEST_IMAGE}
                                    docker logout
                                """
                            }
                        }
                    }
                }
            }
        }

        // ── Stage 6: Deploy ───────────────────────────────────────────
        stage('Deploy') {
            steps {
                echo "━━━ Stage 6: Deploying container ━━━"
                script {
                    if (isUnix()) {
                        sh """
                            docker volume create ${DATA_VOLUME} || true
                            docker network create student-management_monitoring-net || true
                            docker stop ${CONTAINER_NAME} || true
                            docker rm   ${CONTAINER_NAME} || true
                            docker run -d --name ${CONTAINER_NAME} --restart unless-stopped --network student-management_monitoring-net --network-alias app -p ${APP_PORT}:5000 -v ${DATA_VOLUME}:/app/data ${LATEST_IMAGE}
                            sleep 4
                            docker ps
                        """
                    } else {
                        bat """
                            docker volume create ${DATA_VOLUME} || verify > nul
                            docker network create student-management_monitoring-net || verify > nul
                            docker stop ${CONTAINER_NAME} || verify > nul
                            docker rm   ${CONTAINER_NAME} || verify > nul
                            docker run -d --name ${CONTAINER_NAME} --restart unless-stopped --network student-management_monitoring-net --network-alias app -p ${APP_PORT}:5000 -v ${DATA_VOLUME}:/app/data ${LATEST_IMAGE}
                            timeout /t 4 /nobreak > nul
                            docker ps
                        """
                    }
                }
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
        unstable {
            echo """
            ╔══════════════════════════════════════════════════╗
            ║  ⚠ PIPELINE UNSTABLE (Expected in Demo)          ║
            ║  Tests & Build Passed, Docker Push skipped       ║
            ║  App URL: http://localhost:${APP_PORT}           ║
            ╚══════════════════════════════════════════════════╝
            """
        }
        failure {
            echo """
            ╔══════════════════════════════════════════════════╗
            ║  ✗ PIPELINE FAILED — Build #${BUILD_NUMBER}      ║
            ╚══════════════════════════════════════════════════╝
            """
        }
        always {
            script {
                if (isUnix()) {
                    sh 'rm -rf venv || true'
                } else {
                    bat 'if exist venv rmdir /s /q venv'
                }
            }
            echo 'Pipeline finished.'
        }
    }

}
