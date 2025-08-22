pipeline {
  agent any
  options { timestamps() }

  environment {
    // Kontainer jalan via DinD
    DOCKER_HOST    = 'tcp://dind:2375'

    // Akses SonarQube via IP (network 'jenkins' milik daemon host)
    SONAR_HOST_URL = 'http://172.18.0.4:9000'

    // Semgrep
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

    stage('Docker Daemon Check') {
      steps {
        sh 'echo DOCKER_HOST=$DOCKER_HOST'
        sh 'docker version'   // harus tampil Client + Server (Server = DinD)
      }
    }

    stage('Connectivity: SonarQube from DinD') {
      steps {
        // Uji koneksi ke Sonar dari kontainer yang DIJALANKAN oleh DinD
        sh 'docker run --rm curlimages/curl -s "$SONAR_HOST_URL/api/system/status"'
      }
    }

    stage('SonarQube Scan (Docker CLI + token)') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
          sh '''
            export SONAR_LOGIN="$SONAR_TOKEN"
            docker pull sonarsource/sonar-scanner-cli
            docker run --rm -v "$PWD:/usr/src" \
              -e SONAR_HOST_URL="$SONAR_HOST_URL" -e SONAR_LOGIN="$SONAR_LOGIN" \
              sonarsource/sonar-scanner-cli \
                -Dsonar.host.url="$SONAR_HOST_URL" \
                -Dsonar.login="$SONAR_LOGIN" \
                -Dsonar.projectKey=kecilin:testing-sast-devsecops \
                -Dsonar.projectName=testing-sast-devsecops \
                -Dsonar.sources=src \
                -Dsonar.inclusions=src/** \
                -Dsonar.exclusions="**/log/**,**/log4/**,**/log_3/**,**/*.test.*,**/node_modules/**,**/dist/**,**/build/**,docker-compose.yaml" \
                -Dsonar.coverage.exclusions="**/*.test.*,**/test/**,**/tests**"
          '''
        }
      }
    }

    stage('Semgrep SAST') {
      steps {
        sh """
          docker pull ${SEMGREP_IMAGE}
          docker run --rm -v "$PWD:/src" -w /src \
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
          // Perlu plugin Warnings NG & JUnit
          recordIssues(enabledForFailure: true, tools: [sarif(pattern: "${SEMGREP_SARIF}", id: 'Semgrep')])
          junit allowEmptyResults: true, testResults: "${SEMGREP_JUNIT}"
          archiveArtifacts artifacts: "${SEMGREP_SARIF}, ${SEMGREP_JUNIT}", fingerprint: true, onlyIfSuccessful: false
        }
      }
    }
  }

  post {
    always  { echo "Build result: ${currentBuild.currentResult}" }
    failure { echo "Cek temuan SonarQube & Semgrep di halaman build." }
  }
}
