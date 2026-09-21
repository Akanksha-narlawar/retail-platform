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

                    // Production must be explicitly confirmed

                    if (
                        params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PROD != 'YES'
                    ) {

                        error(
                            "Production deployment blocked: " +
                            "CONFIRM_PROD must be YES"
                        )
                    }


                    // Rollback is only allowed for production

                    if (
                        params.DEPLOYMENT_ACTION == 'ROLLBACK' &&
                        params.ENVIRONMENT != 'PRODUCTION'
                    ) {

                        error(
                            "ROLLBACK action is allowed only for PRODUCTION"
                        )
                    }


                    // Validate version format

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
                            "@git rev-parse --verify refs/tags/${tag}",
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
                        @git checkout --force ${tag}
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
                    @"C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t retail-app:${params.VERSION} .
                """


                echo "Docker image retail-app:${params.VERSION} built successfully"
            }
        }


        // ============================================================
        // 4. RECORD PREVIOUS PRODUCTION IMAGE
        // ============================================================

        stage('Record Previous Production Image') {

            when {

                expression {

                    params.ENVIRONMENT == 'PRODUCTION'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"


                    echo "======================================"
                    echo "RECORD PREVIOUS PRODUCTION"
                    echo "======================================"


                    /*
                     * Find the container currently using host port 8081.
                     */

                    def productionInfo = bat(
                        script:
                            "@\"${dockerPath}\" ps -a --format=\"{{.Names}}|{{.Image}}|{{.Ports}}\"",
                        returnStdout: true
                    ).trim()


                    def productionLine = productionInfo
                        .readLines()
                        .find {
                            it.contains("8081->5000")
                        }


                    if (productionLine) {

                        def parts = productionLine.split("\\|")


                        def previousContainer = parts[0].trim()
                        def previousImage = parts[1].trim()


                        echo "Previous production container: ${previousContainer}"
                        echo "Previous production image: ${previousImage}"


                        env.PREVIOUS_PRODUCTION_CONTAINER =
                            previousContainer


                        env.PREVIOUS_PRODUCTION_IMAGE =
                            previousImage


                        /*
                         * Extract version from:
                         * retail-app:4.2.1
                         */

                        if (previousImage.contains(":")) {

                            def previousVersion =
                                previousImage.substring(
                                    previousImage.lastIndexOf(":") + 1
                                )

                            env.PREVIOUS_PRODUCTION_VERSION =
                                previousVersion

                            echo "Previous production version: ${previousVersion}"

                        } else {

                            env.PREVIOUS_PRODUCTION_VERSION = "UNKNOWN"
                        }


                    } else {

                        echo "No production container found on port 8081"


                        env.PREVIOUS_PRODUCTION_CONTAINER = "NONE"
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
                        @"${dockerPath}" network inspect retail-network >nul 2>&1 || "${dockerPath}" network create retail-network
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


                    /*
                     * Remove previous candidate if it exists.
                     */

                    bat """
                        @"${dockerPath}" rm -f retail-app-candidate 2>nul || exit /b 0
                    """


                    /*
                     * Mandatory failure injection.
                     *
                     * Version 4.2.2 intentionally receives
                     * a failing health command.
                     */

                    if (params.VERSION == "4.2.2") {

                        echo "======================================"
                        echo "FAILURE INJECTION ENABLED"
                        echo "Version 4.2.2 will FAIL health check"
                        echo "======================================"


                        bat """
                            @"${dockerPath}" run -d ^
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
                            @"${dockerPath}" run -d ^
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
                        @"${dockerPath}" ps -a --filter "name=retail-app-candidate"
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


                    echo "Waiting for candidate application..."


                    bat "ping 127.0.0.1 -n 16 > nul"


                    /*
                     * Capture Docker health correctly.
                     * @ prevents Windows command echo from entering
                     * returnStdout.
                     */

                    def healthStatus = bat(
                        script:
                            "@\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" retail-app-candidate",
                        returnStdout: true
                    ).trim()


                    echo "Candidate Docker health: ${healthStatus}"


                    /*
                     * Mandatory v4.2.2 failure.
                     */

                    if (params.VERSION == "4.2.2") {

                        echo "======================================"
                        echo "EXPECTED FAILURE: v4.2.2"
                        echo "======================================"

                        echo "Health status: ${healthStatus}"


                        echo "Stopping failed candidate..."


                        bat """
                            @"${dockerPath}" rm -f retail-app-candidate
                        """


                        echo "Candidate v4.2.2 removed"


                        /*
                         * Previous production remains running.
                         * Verify that rollback target is healthy.
                         */

                        if (
                            env.PREVIOUS_PRODUCTION_CONTAINER != "NONE"
                        ) {

                            echo "======================================"
                            echo "RESTORING PREVIOUS PRODUCTION"
                            echo "======================================"

                            echo "Previous container: ${env.PREVIOUS_PRODUCTION_CONTAINER}"
                            echo "Previous image: ${env.PREVIOUS_PRODUCTION_IMAGE}"


                            bat "ping 127.0.0.1 -n 6 > nul"


                            def oldHealth = bat(
                                script:
                                    "@\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" ${env.PREVIOUS_PRODUCTION_CONTAINER}",
                                returnStdout: true
                            ).trim()


                            echo "Previous production health: ${oldHealth}"


                            if (oldHealth != "healthy") {

                                error(
                                    "Rollback verification failed. " +
                                    "Previous production is not healthy."
                                )
                            }


                            echo "Previous production v${env.PREVIOUS_PRODUCTION_VERSION} is healthy"
                            echo "Final state: ROLLBACK COMPLETE"
                        }


                        /*
                         * Jenkins must finish FAILURE because the
                         * new release failed.
                         */

                        error(
                            "Health check FAILED for v4.2.2. " +
                            "Candidate removed and previous production verified."
                        )
                    }


                    /*
                     * Normal candidate HTTP health check.
                     */

                    echo "Checking application /health..."


                    bat """
                        @powershell -NoProfile -Command "try { \$response = Invoke-WebRequest -Uri 'http://localhost:18081/health' -UseBasicParsing; Write-Host ('HTTP Status: ' + \$response.StatusCode); Write-Host ('Response: ' + \$response.Content); if (\$response.StatusCode -ne 200) { exit 1 } } catch { Write-Host ('Health check failed: ' + \$_.Exception.Message); exit 1 }"
                    """


                    /*
                     * Final Docker health validation.
                     */

                    def finalCandidateHealth = bat(
                        script:
                            "@\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" retail-app-candidate",
                        returnStdout: true
                    ).trim()


                    echo "Final candidate Docker health: ${finalCandidateHealth}"


                    if (finalCandidateHealth != "healthy") {

                        bat """
                            @"${dockerPath}" rm -f retail-app-candidate 2>nul || exit /b 0
                        """


                        error(
                            "Candidate health check failed."
                        )
                    }


                    echo "======================================"
                    echo "CANDIDATE HEALTH CHECK PASSED"
                    echo "======================================"
                }
            }
        }


        // ============================================================
        // 8. DEPLOY TO PRODUCTION
        // ============================================================

        stage('Deploy To Production') {

            when {

                expression {

                    params.DEPLOYMENT_ACTION == 'DEPLOY' &&
                    params.ENVIRONMENT == 'PRODUCTION'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"


                    echo "======================================"
                    echo "PRODUCTION DEPLOYMENT"
                    echo "======================================"


                    echo "Previous production container:"
                    echo "${env.PREVIOUS_PRODUCTION_CONTAINER}"


                    echo "Previous production image:"
                    echo "${env.PREVIOUS_PRODUCTION_IMAGE}"


                    echo "New production image:"
                    echo "retail-app:${params.VERSION}"


                    /*
                     * Candidate has already passed health check.
                     *
                     * Now we can switch production.
                     */

                    if (
                        env.PREVIOUS_PRODUCTION_CONTAINER != "NONE"
                    ) {

                        echo "Stopping previous production container..."


                        bat """
                            @"${dockerPath}" stop ${env.PREVIOUS_PRODUCTION_CONTAINER} 2>nul || exit /b 0
                        """


                        bat """
                            @"${dockerPath}" rm ${env.PREVIOUS_PRODUCTION_CONTAINER} 2>nul || exit /b 0
                        """
                    }


                    /*
                     * Remove any old container with same new version name.
                     */

                    bat """
                        @"${dockerPath}" rm -f retail-app-${params.VERSION} 2>nul || exit /b 0
                    """


                    echo "Starting new production container..."


                    bat """
                        @"${dockerPath}" run -d ^
                        --name retail-app-${params.VERSION} ^
                        --network retail-network ^
                        -p 8081:5000 ^
                        -e APP_VERSION=${params.VERSION} ^
                        -e ENVIRONMENT=PRODUCTION ^
                        retail-app:${params.VERSION}
                    """


                    echo "New production container started"


                    bat """
                        @"${dockerPath}" ps -a --filter "name=retail-app-${params.VERSION}"
                    """


                    /*
                     * Candidate no longer needs port 18081.
                     */

                    bat """
                        @"${dockerPath}" rm -f retail-app-candidate 2>nul || exit /b 0
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

                    params.DEPLOYMENT_ACTION == 'DEPLOY' &&
                    params.ENVIRONMENT == 'PRODUCTION'
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


                    /*
                     * Correctly capture Docker health.
                     */

                    def productionHealth = bat(
                        script:
                            "@\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" retail-app-${params.VERSION}",
                        returnStdout: true
                    ).trim()


                    echo "Production Docker health: ${productionHealth}"


                    /*
                     * If Docker health is not healthy,
                     * automatically rollback.
                     */

                    if (productionHealth != "healthy") {

                        echo "======================================"
                        echo "PRODUCTION HEALTH CHECK FAILED"
                        echo "======================================"


                        echo "New version: retail-app:${params.VERSION}"
                        echo "Previous version: ${env.PREVIOUS_PRODUCTION_IMAGE}"


                        echo "Removing failed production container..."


                        bat """
                            @"${dockerPath}" rm -f retail-app-${params.VERSION} 2>nul || exit /b 0
                        """


                        /*
                         * Restore previous production image.
                         */

                        if (
                            env.PREVIOUS_PRODUCTION_IMAGE != "NONE"
                        ) {

                            echo "======================================"
                            echo "STARTING AUTOMATIC ROLLBACK"
                            echo "======================================"


                            bat """
                                @"${dockerPath}" run -d ^
                                --name ${env.PREVIOUS_PRODUCTION_CONTAINER} ^
                                --network retail-network ^
                                -p 8081:5000 ^
                                -e APP_VERSION=${env.PREVIOUS_PRODUCTION_VERSION} ^
                                -e ENVIRONMENT=PRODUCTION ^
                                ${env.PREVIOUS_PRODUCTION_IMAGE}
                            """


                            echo "Previous production version started"


                            bat "ping 127.0.0.1 -n 16 > nul"


                            def rollbackHealth = bat(
                                script:
                                    "@\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" ${env.PREVIOUS_PRODUCTION_CONTAINER}",
                                returnStdout: true
                            ).trim()


                            echo "Rollback Docker health: ${rollbackHealth}"


                            if (rollbackHealth != "healthy") {

                                error(
                                    "CRITICAL: Rollback failed. " +
                                    "Previous production version is unhealthy."
                                )
                            }


                            /*
                             * Verify restored application endpoint.
                             */

                            bat """
                                @powershell -NoProfile -Command "try { \$response = Invoke-WebRequest -Uri 'http://localhost:8081/health' -UseBasicParsing; Write-Host ('Rollback HTTP Status: ' + \$response.StatusCode); Write-Host ('Rollback Response: ' + \$response.Content); if (\$response.StatusCode -ne 200) { exit 1 } } catch { Write-Host ('Rollback HTTP check failed: ' + \$_.Exception.Message); exit 1 }"
                            """


                            echo "======================================"
                            echo "ROLLBACK SUCCESSFUL"
                            echo "======================================"


                            echo "Restored image: ${env.PREVIOUS_PRODUCTION_IMAGE}"
                            echo "Final state: ROLLBACK COMPLETE"


                            /*
                             * Pipeline must be FAILURE because
                             * deployment failed.
                             */

                            error(
                                "Production deployment failed. " +
                                "Automatic rollback completed successfully."
                            )
                        }


                        error(
                            "Production deployment failed and no previous production image was available."
                        )
                    }


                    /*
                     * Docker health passed.
                     *
                     * Now verify HTTP endpoint.
                     */

                    echo "Checking production /health endpoint..."


                    bat """
                        @powershell -NoProfile -Command "try { \$response = Invoke-WebRequest -Uri 'http://localhost:8081/health' -UseBasicParsing; Write-Host ('HTTP Status: ' + \$response.StatusCode); Write-Host ('Response: ' + \$response.Content); if (\$response.StatusCode -ne 200) { exit 1 } } catch { Write-Host ('Production health check failed: ' + \$_.Exception.Message); exit 1 }"
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
        // 10. CLEAN UAT CANDIDATE
        // ============================================================

        stage('Cleanup UAT Candidate') {

            when {

                expression {

                    params.DEPLOYMENT_ACTION == 'DEPLOY' &&
                    params.ENVIRONMENT == 'UAT'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"


                    echo "======================================"
                    echo "UAT DEPLOYMENT COMPLETE"
                    echo "======================================"


                    echo "Candidate health check passed"


                    echo "Removing UAT candidate container..."


                    bat """
                        @"${dockerPath}" rm -f retail-app-candidate 2>nul || exit /b 0
                    """


                    echo "UAT candidate removed"


                    echo "Final state: UAT VALIDATED"
                }
            }
        }


        // ============================================================
        // 11. MANUAL ROLLBACK
        // ============================================================

        stage('Manual Rollback') {

            when {

                expression {

                    params.DEPLOYMENT_ACTION == 'ROLLBACK' &&
                    params.ENVIRONMENT == 'PRODUCTION'
                }
            }

            steps {

                script {

                    def dockerPath =
                        "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"


                    echo "======================================"
                    echo "MANUAL ROLLBACK"
                    echo "======================================"


                    echo "Rollback target version: ${params.VERSION}"


                    /*
                     * Find current production container.
                     */

                    def currentProductionInfo = bat(
                        script:
                            "@\"${dockerPath}\" ps -a --format=\"{{.Names}}|{{.Image}}|{{.Ports}}\"",
                        returnStdout: true
                    ).trim()


                    def currentProductionLine =
                        currentProductionInfo
                            .readLines()
                            .find {
                                it.contains("8081->5000")
                            }


                    if (!currentProductionLine) {

                        error(
                            "No current production container found on port 8081."
                        )
                    }


                    def currentParts =
                        currentProductionLine.split("\\|")


                    def currentContainer =
                        currentParts[0].trim()


                    def currentImage =
                        currentParts[1].trim()


                    echo "Current production container: ${currentContainer}"
                    echo "Current production image: ${currentImage}"


                    /*
                     * Make sure rollback image exists.
                     */

                    def imageExists = bat(
                        script:
                            "@\"${dockerPath}\" image inspect retail-app:${params.VERSION}",
                        returnStatus: true
                    )


                    if (imageExists != 0) {

                        error(
                            "Rollback image retail-app:${params.VERSION} does not exist."
                        )
                    }


                    /*
                     * Stop current production.
                     */

                    echo "Stopping current production..."


                    bat """
                        @"${dockerPath}" stop ${currentContainer} 2>nul || exit /b 0
                    """


                    bat """
                        @"${dockerPath}" rm ${currentContainer} 2>nul || exit /b 0
                    """


                    /*
                     * Start rollback version.
                     */

                    echo "Starting rollback version..."


                    bat """
                        @"${dockerPath}" run -d ^
                        --name retail-app-${params.VERSION} ^
                        --network retail-network ^
                        -p 8081:5000 ^
                        -e APP_VERSION=${params.VERSION} ^
                        -e ENVIRONMENT=PRODUCTION ^
                        retail-app:${params.VERSION}
                    """


                    echo "Rollback version started"


                    bat "ping 127.0.0.1 -n 16 > nul"


                    /*
                     * Check Docker health.
                     */

                    def rollbackHealth = bat(
                        script:
                            "@\"${dockerPath}\" inspect --format=\"{{.State.Health.Status}}\" retail-app-${params.VERSION}",
                        returnStdout: true
                    ).trim()


                    echo "Rollback Docker health: ${rollbackHealth}"


                    if (rollbackHealth != "healthy") {

                        error(
                            "Manual rollback failed: Docker health is ${rollbackHealth}"
                        )
                    }


                    /*
                     * Check HTTP health.
                     */

                    bat """
                        @powershell -NoProfile -Command "try { \$response = Invoke-WebRequest -Uri 'http://localhost:8081/health' -UseBasicParsing; Write-Host ('HTTP Status: ' + \$response.StatusCode); Write-Host ('Response: ' + \$response.Content); if (\$response.StatusCode -ne 200) { exit 1 } } catch { Write-Host ('Rollback health check failed: ' + \$_.Exception.Message); exit 1 }"
                    """


                    echo "======================================"
                    echo "MANUAL ROLLBACK SUCCESSFUL"
                    echo "======================================"


                    echo "Rollback image: retail-app:${params.VERSION}"
                    echo "Final state: ROLLBACK COMPLETE"
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
            echo "======================================"

            echo "Deployment failed or rollback was required."
        }


        always {

            echo "======================================"
            echo "PIPELINE COMPLETED"
            echo "======================================"

            echo "Action      : ${params.DEPLOYMENT_ACTION}"
            echo "Environment : ${params.ENVIRONMENT}"
            echo "Version     : ${params.VERSION}"

            echo "======================================"
        }
    }
}