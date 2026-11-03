pipeline {
    agent any
    environment {
        PYTHONUNBUFFERED = '1'
        REGISTRY_NAME  = 'python-crud-api'
        CONTAINER_NAME = 'production-api-container'
        PORT_MAPPING   = '5000:5000'
        VOLUME_NAME    = 'production-api-data'
    }
    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
                script {
                    env.GIT_SHORT = sh(returnStdout: true,
                        script: 'git rev-parse --short HEAD').trim()
                }
            }
        }
        stage('2. Build Docker Image') {
            steps {
                sh 'docker build -t ${REGISTRY_NAME}:${BUILD_NUMBER} .'
                sh 'docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:${GIT_SHORT}'
                sh 'docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:latest'
            }
        }
        stage('3. Syntax Check & Unit Test') {
            steps {
                sh 'docker run --rm ${REGISTRY_NAME}:${BUILD_NUMBER} python -m py_compile app.py'
                sh 'docker run --rm ${REGISTRY_NAME}:${BUILD_NUMBER} python -m unittest -v test_app'
            }
        }
        stage('4. Automated Deployment') {
            steps {
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker volume create ${VOLUME_NAME}
                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      -p ${PORT_MAPPING} \
                      -v ${VOLUME_NAME}:/var/lib/backend_data \
                      ${REGISTRY_NAME}:latest
                '''
            }
        }
        stage('5. Health Check') {
            steps {
                sh 'sleep 5'
                sh '''docker exec ${CONTAINER_NAME} python -c "import urllib.request as u; print(u.urlopen('http://localhost:5000/health').read().decode())"'''
                sh 'docker inspect --format="{{.State.Health.Status}}" ${CONTAINER_NAME}'
                sh 'docker logs --tail 20 ${CONTAINER_NAME}'
            }
        }
    }
    post {
        success { echo 'Pipeline completed successfully.' }
        failure { echo 'Pipeline failed. Inspect Console Output.' }
    }
}