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
                echo "Deployment Action: ${params.DEPLOYMENT_ACTION}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Version: ${params.VERSION}"
                echo "Production Confirmation: ${params.CONFIRM_PROD}"

                script {
                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PROD != 'YES') {
                        error("Production deployment blocked: CONFIRM_PROD must be YES")
                    }
                }
            }
        }

        stage('Validate Git Version') {
            steps {
                script {
                    def tag = "v${params.VERSION}"

                    echo "Checking Git tag: ${tag}"

                    def tagExists = bat(
                        script: "git tag --list ${tag}",
                        returnStdout: true
                    ).trim()

                    if (tagExists != tag) {
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
    }
}