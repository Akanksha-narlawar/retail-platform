pipeline {
    agent any

    parameters {
        choice(
            name: 'DEPLOYMENT_ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'Choose deployment action'
        )

        choice(
            name: 'ENVIRONMENT',
            choices: ['UAT', 'PRODUCTION'],
            description: 'Choose deployment environment'
        )

        string(
            name: 'VERSION',
            defaultValue: '4.2.1',
            description: 'Docker/Git version to deploy'
        )

        choice(
            name: 'CONFIRM_PROD',
            choices: ['NO', 'YES'],
            description: 'Production deployment confirmation'
        )
    }

    stages {

        // ============================================================
        // 1. VALIDATE PARAMETERS
        // ============================================================

        stage('Validate Parameters') {
            steps {

                echo "======================================"
                echo "DEPLOYMENT PARAMETERS"
                echo "======================================"
                echo "Deployment Action : ${params.DEPLOYMENT_ACTION}"
                echo "Environment       : ${params.ENVIRONMENT}"
                echo "Version           : ${params.VERSION}"
                echo "Production Confirm: ${params.CONFIRM_PROD}"
                echo "======================================"

                script {

                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PROD != 'YES') {

                        error(
                            "Production deployment blocked: " +
                            "CONFIRM_PROD must be YES"
                        )
                    }

                    if (!(params.VERSION ==~ /^\d+\.\d+\.\d+$/)) {

                        error(
                            "Invalid version format: ${params.VERSION}. " +
                            "Expected format: X.Y.Z"
                        )
                    }
                }
            }
        }


        // ============================================================
        // 2. VALIDATE GIT VERSION
        // ============================================================

        stage('Validate Git Version') {

            steps {

                script {

                    def tag = "v${params.VERSION}"

                    echo "======================================"
                    echo "GIT VERSION VALIDATION"
                    echo "======================================"

                    echo "Fetching Git tags..."

                    bat "git fetch --tags --force"

                    echo "Checking Git tag: ${tag}"

                    def tagExists = bat(
                        script:
                            "git rev-parse --verify refs/tags/${tag}",
                        returnStatus: true
                    )

                    if (tagExists != 0) {

                        error(
                            "Git tag ${tag} does not exist"
                        )
                    }

                    echo "Git tag ${tag} exists"

                    def commitId = bat(
                        script:
                            "@git rev-list -n 1 ${tag}",
                        returnStdout: true
                    ).trim()

                    echo "Selected Git commit: ${commitId}"

                    echo "Checking out selected Git version: ${tag}"

                    bat """
                        git checkout --force ${tag}
                    """

                    echo "Git version ${tag} checked out successfully"
                }
            }
        }


        // ============================================================
        // 3. BUILD DOCKER IMAGE
        // ============================================================

        stage('Build Docker Image') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                echo "======================================"
                echo "BUILDING DOCKER IMAGE"
                echo "======================================"

                echo "Image: retail-app:${params.VERSION}"

                bat """
                    "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t retail-app:${params.VERSION} .
                """

                echo "Docker image retail-app:${params.VERSION} built successfully"
            }
        }


        // ============================================================
        // 4. RECORD PREVIOUS PRODUCTION IMAGE
        // ============================================================

        stage('Record Previous Production Image') {

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "PREVIOUS PRODUCTION VERSION"
                    echo "======================================"

                    bat """
                        "${dockerPath}" ps -a
                    """

                    def productionContainer = bat(
                        script:
                            "\"${dockerPath}\" ps -a --filter \"name=retail-app-4.2.1\" --format \"{{.Names}}\"",
                        returnStdout: true
                    ).trim()

                    if (productionContainer.contains("retail-app-4.2.1")) {

                        def previousImage = bat(
                            script:
                                "\"${dockerPath}\" inspect --format=\"{{.Config.Image}}\" retail-app-4.2.1",
                            returnStdout: true
                        ).trim()

                        echo "Previous production container: retail-app-4.2.1"
                        echo "Previous production image: ${previousImage}"

                        env.PREVIOUS_PRODUCTION_IMAGE =
                            "retail-app:4.2.1"

                        env.PREVIOUS_PRODUCTION_VERSION =
                            "4.2.1"

                    } else {

                        echo "No previous production container found"

                        env.PREVIOUS_PRODUCTION_IMAGE = "NONE"
                        env.PREVIOUS_PRODUCTION_VERSION = "NONE"
                    }
                }
            }
        }


        // ============================================================
        // 5. PREPARE DOCKER NETWORK
        // ============================================================

        stage('Prepare Docker Network') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "PREPARING DOCKER NETWORK"
                    echo "======================================"

                    bat """
                        "${dockerPath}" network inspect retail-network >nul 2>&1 || "${dockerPath}" network create retail-network
                    """

                    echo "Docker network retail-network is ready"
                }
            }
        }


        // ============================================================
        // 6. DEPLOY CANDIDATE
        // ============================================================

        stage('Deploy Candidate') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "STARTING CANDIDATE CONTAINER"
                    echo "======================================"

                    bat """
                        "${dockerPath}" rm -f retail-app-candidate 2>nul || exit /b 0
                    """

                    /*
                     * v4.2.2 is intentionally configured to fail
                     * the health check.
                     *
                     * This is required by the assessment.
                     */

                    if (params.VERSION == "4.2.2") {

                        echo "======================================"
                        echo "FAILURE INJECTION ENABLED"
                        echo "Version 4.2.2 will fail health check"
                        echo "======================================"

                        bat """
                            "${dockerPath}" run -d ^
                            --name retail-app-candidate ^
                            --network retail-network ^
                            -p 18081:5000 ^
                            -e APP_VERSION=${params.VERSION} ^
                            -e ENVIRONMENT=${params.ENVIRONMENT} ^
                            --health-cmd="exit 1" ^
                            --health-interval=10s ^
                            --health-timeout=5s ^
                            --health-retries=3 ^
                            retail-app:${params.VERSION}
                        """

                    } else {

                        bat """
                            "${dockerPath}" run -d ^
                            --name retail-app-candidate ^
                            --network retail-network ^
                            -p 18081:5000 ^
                            -e APP_VERSION=${params.VERSION} ^
                            -e ENVIRONMENT=${params.ENVIRONMENT} ^
                            retail-app:${params.VERSION}
                        """
                    }

                    echo "Candidate container started"

                    bat """
                        "${dockerPath}" ps -a --filter "name=retail-app-candidate"
                    """
                }
            }
        }


        // ============================================================
        // 7. HEALTH CHECK CANDIDATE
        // ============================================================

        stage('Health Check Candidate') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "CANDIDATE HEALTH CHECK"
                    echo "======================================"

                    echo "Waiting 15 seconds for application..."

                    bat "ping 127.0.0.1 -n 16 > nul"

                    def healthStatus = bat(
                        script:
                            "\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" retail-app-candidate",
                        returnStdout: true
                    ).trim()

                    echo "Candidate Docker health: ${healthStatus}"

                    /*
                     * Mandatory failure injection:
                     * v4.2.2 must fail here.
                     */

                    if (params.VERSION == "4.2.2") {

                        echo "======================================"
                        echo "EXPECTED FAILURE: v4.2.2"
                        echo "======================================"

                        bat """
                            "${dockerPath}" inspect --format="{{.State.Health.Status}}" retail-app-candidate
                        """

                        echo "Stopping failed candidate..."

                        bat """
                            "${dockerPath}" rm -f retail-app-candidate
                        """

                        echo "======================================"
                        echo "ROLLBACK REQUIRED"
                        echo "Previous production image: ${env.PREVIOUS_PRODUCTION_IMAGE}"
                        echo "======================================"

                        error(
                            "Health check FAILED for v4.2.2. " +
                            "Automatic rollback is required."
                        )
                    }


                    echo "Checking application /health..."

                    bat """
                        powershell -NoProfile -Command "try { \$response = Invoke-WebRequest -Uri 'http://localhost:18081/health' -UseBasicParsing; Write-Host ('HTTP Status: ' + \$response.StatusCode); Write-Host ('Response: ' + \$response.Content); if (\$response.StatusCode -ne 200) { exit 1 } } catch { Write-Host ('Health check failed: ' + \$_.Exception.Message); exit 1 }"
                    """

                    echo "Checking Docker health..."

                    bat """
                        "${dockerPath}" inspect --format="{{.State.Health.Status}}" retail-app-candidate
                    """

                    echo "Candidate health check PASSED"
                }
            }
        }


        // ============================================================
        // 8. SWITCH CANDIDATE TO PRODUCTION
        // ============================================================

        stage('Deploy To Production') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "PRODUCTION DEPLOYMENT"
                    echo "======================================"

                    echo "Previous production image:"
                    echo "${env.PREVIOUS_PRODUCTION_IMAGE}"

                    echo "New production image:"
                    echo "retail-app:${params.VERSION}"


                    echo "Stopping previous production container..."

                    bat """
                        "${dockerPath}" stop retail-app-4.2.1 2>nul || exit /b 0
                    """

                    bat """
                        "${dockerPath}" rm retail-app-4.2.1 2>nul || exit /b 0
                    """


                    echo "Starting new production container..."

                    bat """
                        "${dockerPath}" rm -f retail-app-${params.VERSION} 2>nul || exit /b 0
                    """

                    bat """
                        "${dockerPath}" run -d ^
                        --name retail-app-${params.VERSION} ^
                        --network retail-network ^
                        -p 8081:5000 ^
                        -e APP_VERSION=${params.VERSION} ^
                        -e ENVIRONMENT=${params.ENVIRONMENT} ^
                        retail-app:${params.VERSION}
                    """

                    echo "New production container started"

                    bat """
                        "${dockerPath}" ps -a --filter "name=retail-app-${params.VERSION}"
                    """

                    /*
                     * Candidate is no longer needed.
                     */

                    bat """
                        "${dockerPath}" rm -f retail-app-candidate 2>nul || exit /b 0
                    """
                }
            }
        }


        // ============================================================
        // 9. FINAL PRODUCTION HEALTH CHECK
        // ============================================================

        stage('Production Health Check') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "FINAL PRODUCTION HEALTH CHECK"
                    echo "======================================"

                    echo "Waiting for production application..."

                    bat "ping 127.0.0.1 -n 16 > nul"


                    def productionHealth = bat(
                        script:
                            "\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" retail-app-${params.VERSION}",
                        returnStdout: true
                    ).trim()

                    echo "Production Docker health: ${productionHealth}"


                    if (productionHealth != "healthy") {

                        echo "======================================"
                        echo "PRODUCTION HEALTH CHECK FAILED"
                        echo "======================================"

                        echo "New version: retail-app:${params.VERSION}"
                        echo "Previous version: ${env.PREVIOUS_PRODUCTION_IMAGE}"

                        echo "Removing failed production container..."

                        bat """
                            "${dockerPath}" rm -f retail-app-${params.VERSION} 2>nul || exit /b 0
                        """


                        /*
                         * Restore previous production version.
                         */

                        if (env.PREVIOUS_PRODUCTION_IMAGE != "NONE") {

                            echo "Restoring previous production version..."

                            bat """
                                "${dockerPath}" run -d ^
                                --name retail-app-4.2.1 ^
                                --network retail-network ^
                                -p 8081:5000 ^
                                -e APP_VERSION=4.2.1 ^
                                -e ENVIRONMENT=PRODUCTION ^
                                retail-app:4.2.1
                            """

                            echo "Previous version started"

                            bat "ping 127.0.0.1 -n 16 > nul"

                            bat """
                                "${dockerPath}" inspect --format="{{.State.Health.Status}}" retail-app-4.2.1
                            """

                            echo "======================================"
                            echo "ROLLBACK RESTORED v4.2.1"
                            echo "======================================"

                            echo "Final state: ROLLBACK COMPLETE"
                        }

                        error(
                            "Production deployment failed. " +
                            "Rollback was performed."
                        )
                    }


                    echo "Checking production /health endpoint..."

                    bat """
                        powershell -NoProfile -Command "try { \$response = Invoke-WebRequest -Uri 'http://localhost:8081/health' -UseBasicParsing; Write-Host ('HTTP Status: ' + \$response.StatusCode); Write-Host ('Response: ' + \$response.Content); if (\$response.StatusCode -ne 200) { exit 1 } } catch { Write-Host ('Production health check failed: ' + \$_.Exception.Message); exit 1 }"
                    """


                    echo "======================================"
                    echo "PRODUCTION DEPLOYMENT SUCCESSFUL"
                    echo "======================================"

                    echo "Old production image:"
                    echo "${env.PREVIOUS_PRODUCTION_IMAGE}"

                    echo "New production image:"
                    echo "retail-app:${params.VERSION}"

                    echo "Final state: DEPLOYED"
                }
            }
        }


        // ============================================================
        // 10. ROLLBACK ACTION
        // ============================================================

        stage('Manual Rollback') {

            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'ROLLBACK'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "MANUAL ROLLBACK"
                    echo "======================================"

                    echo "Rollback target: ${params.VERSION}"


                    bat """
                        "${dockerPath}" stop retail-app-${params.VERSION} 2>nul || exit /b 0
                    """

                    bat """
                        "${dockerPath}" rm retail-app-${params.VERSION} 2>nul || exit /b 0
                    """


                    bat """
                        "${dockerPath}" rm -f retail-app-rollback 2>nul || exit /b 0
                    """


                    bat """
                        "${dockerPath}" run -d ^
                        --name retail-app-rollback ^
                        --network retail-network ^
                        -p 8081:5000 ^
                        -e APP_VERSION=${params.VERSION} ^
                        -e ENVIRONMENT=PRODUCTION ^
                        retail-app:${params.VERSION}
                    """


                    echo "Rollback container started"

                    bat "ping 127.0.0.1 -n 16 > nul"


                    bat """
                        "${dockerPath}" inspect --format="{{.State.Health.Status}}" retail-app-rollback
                    """


                    bat """
                        powershell -NoProfile -Command "try { \$response = Invoke-WebRequest -Uri 'http://localhost:8081/health' -UseBasicParsing; Write-Host ('HTTP Status: ' + \$response.StatusCode); Write-Host ('Response: ' + \$response.Content); if (\$response.StatusCode -ne 200) { exit 1 } } catch { Write-Host ('Rollback health check failed: ' + \$_.Exception.Message); exit 1 }"
                    """


                    echo "======================================"
                    echo "ROLLBACK SUCCESSFUL"
                    echo "======================================"

                    echo "Final state: ROLLBACK VERSION ${params.VERSION}"
                }
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        success {

            echo "======================================"
            echo "PIPELINE RESULT: SUCCESS"
            echo "======================================"
        }

        failure {

            echo "======================================"
            echo "PIPELINE RESULT: FAILURE"
            echo "Rollback may have been required."
            echo "======================================"
        }

        always {

            echo "======================================"
            echo "PIPELINE COMPLETED"
            echo "Action: ${params.DEPLOYMENT_ACTION}"
            echo "Environment: ${params.ENVIRONMENT}"
            echo "Version: ${params.VERSION}"
            echo "======================================"
        }
    }
}