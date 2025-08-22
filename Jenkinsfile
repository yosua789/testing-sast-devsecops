pipeline {
  agent any
  options { timestamps() }

  // Biar gampang kalau IP Sonar berubah-ubah
  parameters {
    string(name: 'SONAR_HOST_URL', defaultValue: 'http://172.18.0.4:9000',
           description: 'URL SonarQube yang bisa diakses dari kontainer DinD (contoh: http://<IP-Sonar>:9000 atau http://<HOST-IP>:9010)')
  }

  environment {
    // Kontainer job dijalankan oleh DinD
    DOCKER_HOST    = 'tcp://dind:2375'

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
        sh 'docker run --rm curlimages/curl -s -I "${params.SONAR_HOST_URL}" | head -n1 || true'
      }
    }

    stage('SonarQube Scan (CLI + token)') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
          // pakai single-quoted shell block (hindari Groovy interpolation warning)
          sh '''
            docker pull sonarsource/sonar-scanner-cli
            # Mount workspace Jenkins ke dalam kontainer scanner via DinD
            docker run --rm -v "$WORKSPACE:/usr/src" \
              sonarsource/sonar-scanner-cli \
                -Dsonar.host.url="${SONAR_HOST_URL:-''' + "${params.SONAR_HOST_URL}" + '''}" \
                -Dsonar.token="$SONAR_TOKEN" \
                -Dsonar.projectKey=kecilin:testing-sast-devsecops \
                -Dsonar.projectName=testing-sast-devsecops \
                -Dsonar.sources=. \
                -Dsonar.inclusions="**/*" \
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
          docker run --rm -v "$WORKSPACE:/src" -w /src \
            ${SEMGREP_IMAGE} semgrep scan \
            --config p/ci --config p/owasp-top-ten --config p/docker \
            --exclude 'log/**' --exclude 'log4/**' --exclude 'log_3/**' \
            --sarif -o ${SEMGREP_SARIF} \
            --junit-xml --junit-xml-file ${SEMGREP_JUNIT} \
            --severity error --error
        """
      }
      post {
        always {
          // Butuh plugin Warnings NG & JUnit
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
