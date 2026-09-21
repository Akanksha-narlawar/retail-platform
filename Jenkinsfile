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

        stage('Validate Parameters') {
            steps {
                echo "======================================"
                echo "Deployment Action: ${params.DEPLOYMENT_ACTION}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Version: ${params.VERSION}"
                echo "Production Confirmation: ${params.CONFIRM_PROD}"
                echo "======================================"

                script {
                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PROD != 'YES') {

                        error(
                            "Production deployment blocked: " +
                            "CONFIRM_PROD must be YES"
                        )
                    }
                }
            }
        }

        stage('Validate Git Version') {
            steps {
                script {
                    def tag = "v${params.VERSION}"

                    echo "Fetching Git tags..."

                    bat "git fetch --tags --force"

                    echo "Checking Git tag: ${tag}"

                    def tagExists = bat(
                        script: "git rev-parse --verify refs/tags/${tag}",
                        returnStatus: true
                    )

                    if (tagExists != 0) {
                        error("Git tag ${tag} does not exist")
                    }

                    echo "Git tag ${tag} exists"

                    def commitId = bat(
                        script: "git rev-list -n 1 ${tag}",
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

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: retail-app:${params.VERSION}"

                bat """
                    "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t retail-app:${params.VERSION} .
                """

                echo "Docker image retail-app:${params.VERSION} built successfully"
            }
        }

        stage('Record Previous Production Image') {
            steps {
                script {

                    def dockerPath = "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "Docker containers visible to Jenkins:"

                    bat """
                        "${dockerPath}" ps -a
                    """

                    def containerExists = bat(
                        script: "\"${dockerPath}\" ps -a --filter \"name=retail-app-4.2.1\" --format \"{{.Names}}\"",
                        returnStdout: true
                    ).trim()

                    if (containerExists.contains("retail-app-4.2.1")) {

                        def previousImage = bat(
                            script: "\"${dockerPath}\" inspect --format=\"{{.Config.Image}}\" retail-app-4.2.1",
                            returnStdout: true
                        ).trim()

                        echo "Previous production container: retail-app-4.2.1"
                        echo "Previous production image: ${previousImage}"

                        env.PREVIOUS_PRODUCTION_IMAGE = previousImage

                    } else {

                        echo "No previous production container found"
                        env.PREVIOUS_PRODUCTION_IMAGE = "NONE"
                    }
                }
            }
        }

        stage('Deploy New Version Container') {
            steps {
                script {

                    def dockerPath = "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "Preparing Docker network"
                    echo "======================================"

                    bat """
                        "${dockerPath}" network inspect retail-network >nul 2>&1 || "${dockerPath}" network create retail-network
                    """

                    echo "Docker network retail-network is ready"

                    echo "======================================"
                    echo "Starting new version container"
                    echo "======================================"

                    bat """
                        "${dockerPath}" rm -f retail-app-candidate 2>nul || exit /b 0
                    """

                    bat """
                        "${dockerPath}" run -d ^
                        --name retail-app-candidate ^
                        --network retail-network ^
                        -p 18081:5000 ^
                        -e APP_VERSION=${params.VERSION} ^
                        -e ENVIRONMENT=${params.ENVIRONMENT} ^
                        retail-app:${params.VERSION}
                    """

                    echo "New version container started successfully"

                    echo "Candidate container status:"

                    bat """
                        "${dockerPath}" ps -a --filter "name=retail-app-candidate"
                    """
                }
            }
        }

        stage('Health Check New Version') {
            steps {
                script {

                    def dockerPath = "C:\\Users\\akank\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"

                    echo "======================================"
                    echo "Waiting for new container health check"
                    echo "======================================"

                    bat """
                        "${dockerPath}" inspect --format="{{.State.Health.Status}}" retail-app-candidate
                    """

                    echo "Checking application health..."

                    bat """
                        powershell -Command ^
                        "\$response = Invoke-WebRequest -Uri 'http://localhost:18081/health' -UseBasicParsing; ^
                        Write-Host 'HTTP Status:' \$response.StatusCode; ^
                        Write-Host 'Response:' \$response.Content; ^
                        if (\$response.StatusCode -ne 200) { exit 1 }"
                    """

                    echo "New version health check PASSED"
                }
            }
        }

    }
}