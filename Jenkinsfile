pipeline {
    agent any

    environment {
        IMAGE_NAME = "mnaiem262/my-python-app"
        DOCKER_CREDENTIALS_ID = "dockerhub"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    COMMIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    IMAGE_TAG = "${IMAGE_NAME}:${COMMIT_SHA}"
                    env.IMAGE_TAG = IMAGE_TAG
                }
                sh 'docker build -t $IMAGE_TAG .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                    sh 'docker push $IMAGE_TAG'
                    sh 'docker tag $IMAGE_TAG $IMAGE_NAME:latest'
                    sh 'docker push $IMAGE_NAME:latest'
                }
            }
        }

        stage('Deploy Locally') {
            steps {
                script {
                    sh """
                      docker stop my-python-app || true
                      docker rm my-python-app || true
                      docker pull $IMAGE_TAG
                      docker run -d --name my-python-app -p 5000:5000 $IMAGE_TAG
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline complete: $IMAGE_TAG deployed."
        }
    }
}
