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
        KUBECONFIG = '/home/mnaeem/.kube/config'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
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
                    def commitSha = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    def imageTag = "${IMAGE_NAME}:${commitSha}"
                    echo "🏗️ Building Docker image with tag: ${imageTag}"
                    sh "docker build -t ${imageTag} ."
                    // Stash the tag for reuse
                    writeFile file: 'image_tag.txt', text: imageTag
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    def imageTag = readFile('image_tag.txt').trim()
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        '''
                        sh "docker push ${imageTag}"
                        sh "docker tag ${imageTag} ${IMAGE_NAME}:latest"
                        sh "docker push ${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Deploy Locally via Docker') {
            steps {
                script {
                    def imageTag = readFile('image_tag.txt').trim()
                    sh """
                        docker stop my-python-app || true
                        docker rm my-python-app || true
                        docker pull ${imageTag}
                        docker run -d --name my-python-app -p 5000:5000 ${imageTag}
                    """
                }
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
                def imageTag = 'undefined'
                if (fileExists('image_tag.txt')) {
                    imageTag = readFile('image_tag.txt').trim()
                }
                echo imageTag != 'undefined' 
                    ? "✅ Pipeline complete: ${imageTag} deployed and tests passed."
                    : "⚠️ Pipeline ran but IMAGE_TAG not available."
            }
        }

        failure {
            echo "❌ Pipeline failed. Check logs and fix errors."
        }
    }
}
