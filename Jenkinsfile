pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "ngocthinh09/iris-ml-api"
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS_ID = "dockerhub-credentials"

        GKE_CLUSTER = "iris-cluster"
        GKE_ZONE = "asia-southeast1-a"
        GCP_PROJECT = "jenkinscicd-494404"
        GCP_CREDENTIALS_ID = "gcp-auth"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from Github...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python Environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                echo 'Training ML model...'
                sh '''
                    . venv/bin/activate
                    python src/train_model.py
                    cd ..
                '''
            }
        }

        stage('Test Model') {
            steps {
                echo 'Testing model training and predictions...'
                sh '''
                    . venv/bin/activate
                    pytest tests/test_model.py -v --tb=short
                '''
            }
        }

        stage('Test API') {
            steps {
                echo 'Testing FastAPI Application...'
                sh '''
                    . venv/bin/activate
                    pytest tests/test_app.py -v --tb=short
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing to Docker Hub...'
                script {
                    docker.withRegistry('https://registry.hub.docker.com', "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                echo 'Starting deployment to Google Kubernetes Engine...'
                withCredentials([file(credentialsId: "${GCP_CREDENTIALS_ID}", variable: 'GCP_KEY_FILE')]) {
                    sh '''
                        gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}
    
                        gcloud container clusters get-credentials ${GKE_CLUSTER} --zone ${GKE_ZONE} --project ${GCP_PROJECT}
    
                        helm upgrade --install iris-app ./helm/iris-app \
                            --namespace default \
                            --set image.repository=${DOCKER_IMAGE} \
                            --set image.tag=${DOCKER_TAG} \
                            --wait
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                echo 'Cleaning up workspace...'
                sh '''
                    docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                    docker rmi ${DOCKER_IMAGE}:latest || true
                    rm -rf venv
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            echo "Docker Image push successful: ${DOCKER_IMAGE}:${DOCKER_TAG}"
        }

        failure {
            echo 'Pipeline failed. Please check the logs for details.'
        }

        always {
            echo 'Pipeline finished. Cleaning up any remaining resources...'
            cleanWs()
        }
    }
}