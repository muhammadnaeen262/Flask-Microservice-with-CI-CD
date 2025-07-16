// pipeline {
//     agent any

//     environment {
//         IMAGE_NAME = "mnaiem262/my-python-app"
//         DOCKER_CREDENTIALS_ID = "dockerhub"
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }

//         stage('Test') {
//             steps {
//                 sh 'pip install -r requirements.txt'
//                 sh 'pytest tests/'
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     COMMIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
//                     IMAGE_TAG = "${IMAGE_NAME}:${COMMIT_SHA}"
//                     env.IMAGE_TAG = IMAGE_TAG
//                 }
//                 sh 'docker build -t $IMAGE_TAG .'
//             }
//         }

//         stage('Push to Docker Hub') {
//             steps {
//                 withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
//                     sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
//                     sh 'docker push $IMAGE_TAG'
//                     sh 'docker tag $IMAGE_TAG $IMAGE_NAME:latest'
//                     sh 'docker push $IMAGE_NAME:latest'
//                 }
//             }
//         }

//         stage('Deploy to Kubernetes') {
//             steps {
//                 sh """
//                     kubectl apply -f k8s/deployment.yaml
//                     kubectl apply -f k8s/service.yaml
//                 """
//             }
//         }
//     }

//     post {
//         always {
//             echo "Pipeline complete: $IMAGE_TAG deployed."
//         }
//     }
// }
// ============================================================================
// pipeline {
//     agent any

//     environment {
//         IMAGE_NAME = "mnaiem262/my-python-app"
//         DOCKER_CREDENTIALS_ID = "dockerhub"
//         KUBECONFIG = '/var/lib/jenkins/.kube/config'
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }

//         stage('Test') {
//             steps {
//                 sh 'python3 -m venv venv'
//                 sh '. venv/bin/activate && pip install -r requirements.txt && pytest tests/'
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     COMMIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
//                     IMAGE_TAG = "${IMAGE_NAME}:${COMMIT_SHA}"
//                     env.IMAGE_TAG = IMAGE_TAG
//                 }
//                 sh 'docker build -t $IMAGE_TAG .'
//             }
//         }

//         stage('Push to Docker Hub') {
//             steps {
//                 withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
//                     sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
//                     sh 'docker push $IMAGE_TAG'
//                     sh 'docker tag $IMAGE_TAG $IMAGE_NAME:latest'
//                     sh 'docker push $IMAGE_NAME:latest'
//                 }
//             }
//         }

//         stage('Deploy Locally') {
//             steps {
//                 script {
//                     sh """
//                         docker stop my-python-app || true
//                         docker rm my-python-app || true
//                         docker pull $IMAGE_TAG
//                         docker run -d --name my-python-app -p 5000:5000 $IMAGE_TAG
//                     """
//                 }
//             }
//         }
//         stage('Deploy to Kubernetes') {
//             steps {
//                 sh """
//                     kubectl apply -f k8s/deployment.yaml
//                     kubectl apply -f k8s/service.yaml
//                 """
//             }
//         }
//     }

//     post {
//         always {
//             echo "Pipeline complete: $IMAGE_TAG deployed. tests passed."
//         }
//     }
// }
//#####################################################################################
pipeline {
    agent any

    environment {
        IMAGE_NAME = "mnaiem262/my-python-app"
        DOCKER_CREDENTIALS_ID = "dockerhub"
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
        IMAGE_TAG = '' // Will be set in Init stage
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Init Variables') {
            steps {
                script {
                    def commitSha = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    def tag = "${IMAGE_NAME}:${commitSha}"
                    echo "🔖 Commit SHA: ${commitSha}"
                    echo "🔖 Resolved tag: ${tag}"
                    env.IMAGE_TAG = tag
                }
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m venv venv'
                sh '''
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest tests/
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    if (!env.IMAGE_TAG?.trim()) {
                        error("❌ IMAGE_TAG is undefined. Aborting Docker build.")
                    }
                }
                sh '''
                    echo "🏗️ Building Docker image with tag: $IMAGE_TAG"
                    docker build -t $IMAGE_TAG .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "🔐 Logging in to Docker Hub..."
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        echo "📤 Pushing image $IMAGE_TAG"
                        docker push $IMAGE_TAG
                        docker tag $IMAGE_TAG $IMAGE_NAME:latest
                        docker push $IMAGE_NAME:latest
                    '''
                }
            }
        }

        stage('Deploy Locally via Docker') {
            steps {
                sh '''
                    echo "🚀 Deploying locally..."
                    docker stop my-python-app || true
                    docker rm my-python-app || true
                    docker pull $IMAGE_TAG
                    docker run -d --name my-python-app -p 5000:5000 $IMAGE_TAG
                '''
            }
        }

        stage('Deploy to Kubernetes (Minikube)') {
            steps {
                sh '''
                    echo "📦 Deploying to Kubernetes (Minikube)..."
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl apply --validate=false -f k8s/deployment.yaml
                    kubectl apply --validate=false -f k8s/service.yaml
                '''
            }
        }

        stage('Cleanup Docker') {
            steps {
                sh 'docker system prune -f'
            }
        }
    }

    post {
        always {
            script {
                if (env.IMAGE_TAG?.trim()) {
                    echo "✅ Pipeline complete: ${env.IMAGE_TAG} deployed and tests passed."
                } else {
                    echo "⚠️ Pipeline ran but IMAGE_TAG not defined."
                }
            }
        }

        failure {
            echo "❌ Pipeline failed. Check logs and fix errors."
        }
    }
}
