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

    }
}