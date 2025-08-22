pipeline {
  agent any
  options { timestamps() }

  environment {
    DOCKER_HOST    = 'tcp://dind:2375'
    SONAR_HOST_URL = 'http://sonarqube:9000'   // pakai nama ini, akan di-resolve via --add-host
    SEMGREP_IMAGE  = 'semgrep/semgrep:latest'
    SEMGREP_SARIF  = 'semgrep.sarif'
    SEMGREP_JUNIT  = 'semgrep-junit.xml'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git --no-pager log -1 --pretty=oneline || true'
      }
    }

    stage('SonarQube Scan (Docker CLI + token)') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
          sh '''
            export SONAR_LOGIN="$SONAR_TOKEN"
            docker pull sonarsource/sonar-scanner-cli
            docker run --rm \
              --add-host sonarqube:172.18.0.4 \  # <— injek DNS untuk sonarqube
              -v "$PWD:/usr/src" \
              -e SONAR_HOST_URL="$SONAR_HOST_URL" -e SONAR_LOGIN="$SONAR_LOGIN" \
              sonarsource/sonar-scanner-cli \
                -Dsonar.host.url="$SONAR_HOST_URL" \
                -Dsonar.login="$SONAR_LOGIN" \
                -Dsonar.projectKey=kecilin:testing-sast-devsecops \
                -Dsonar.projectName=testing-sast-devsecops \
                -Dsonar.sources=src \
                -Dsonar.inclusions=src/** \
                -Dsonar.exclusions=**/log/**,**/log4/**,**/log_3/**,**/*.test.*,**/node_modules/**,**/dist/**,**/build/**,docker-compose.yaml \
                -Dsonar.coverage.exclusions=**/*.test.*,**/test/**,**/tests**
          '''
        }
      }
    }

    stage('Semgrep SAST') {
      steps {
        sh """
          docker pull ${SEMGREP_IMAGE}
          docker run --rm \
            -v "$PWD:/src" -w /src \
            ${SEMGREP_IMAGE} semgrep scan \
            --config p/ci --config p/owasp-top-ten --config p/docker \
            --include 'src/**' \
            --include 'DockerFile' \
            --exclude 'log/**' --exclude 'log4/**' --exclude 'log_3/**' \
            --sarif -o ${SEMGREP_SARIF} \
            --junit-xml --junit-xml-file ${SEMGREP_JUNIT} \
            --severity error --error
        """
      }
      post {
        always {
          recordIssues(enabledForFailure: true, tools: [sarif(pattern: "${SEMGREP_SARIF}", id: 'Semgrep')])
          junit allowEmptyResults: true, testResults: "${SEMGREP_JUNIT}"
          archiveArtifacts artifacts: "${SEMGREP_SARIF}, ${SEMGREP_JUNIT}", fingerprint: true, onlyIfSuccessful: false
        }
      }
    }
  }

  post {
    always  { echo "Build result: ${currentBuild.currentResult}" }
    failure { echo "Scanning Done" }
  }
}
