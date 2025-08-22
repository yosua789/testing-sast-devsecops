pipeline {
  agent any
  options { timestamps() }

  // Biar gampang kalau URL Sonar berubah
  parameters {
    string(
      name: 'SONAR_HOST_URL',
      defaultValue: 'http://172.18.0.4:9000',   // ganti kalau IP/port Sonar beda
      description: 'URL SonarQube yang bisa diakses dari kontainer DinD'
    )
  }

  environment {
    // Semua "docker run/pull" dijalankan oleh DinD
    DOCKER_HOST    = 'tcp://dind:2375'

    // Semgrep
    SEMGREP_IMAGE  = 'semgrep/semgrep:latest'
    SEMGREP_SARIF  = 'semgrep.sarif'
    SEMGREP_JUNIT  = 'semgrep-junit.xml'

    // Identitas project SonarQube (HARUS sudah ada di Sonar)
    SONAR_PROJECT_KEY  = 'kecilin:testing-sast-devsecops'
    SONAR_PROJECT_NAME = 'testing-sast-devsecops'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git --no-pager log -1 --pretty=oneline || true'
      }
    }

    stage('Docker & Sonar connectivity') {
      steps {
        withEnv(["SONAR_HOST_URL=${params.SONAR_HOST_URL}"]) {
          sh 'echo DOCKER_HOST=$DOCKER_HOST'
          sh 'docker version'   // harus tampil Client + Server (Server = DinD)
          // Cek Sonar reachable dari kontainer (tanpa --network, karena lewat DinD)
          sh 'docker run --rm curlimages/curl -s -I "$SONAR_HOST_URL" | head -n1 || true'
          sh 'docker run --rm curlimages/curl -s "$SONAR_HOST_URL/api/system/status" || true'
        }
      }
    }

    stage('SonarQube Scan') {
      steps {
        withEnv(["SONAR_HOST_URL=${params.SONAR_HOST_URL}"]) {
          withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
            // NOTE: pakai Groovy single-quoted block, variabel shell tetap diexpand karena kita pakai "double quotes" di dalamnya
            sh '''
              docker pull sonarsource/sonar-scanner-cli
              # Repo kamu tidak punya folder src/, jadi sumber = root (.)
              docker run --rm -v "$WORKSPACE:/usr/src" \
                sonarsource/sonar-scanner-cli \
                  -Dsonar.host.url="$SONAR_HOST_URL" \
                  -Dsonar.token="$SONAR_TOKEN" \
                  -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                  -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                  -Dsonar.sources=. \
                  -Dsonar.inclusions="**/*" \
                  -Dsonar.exclusions="**/log/**,**/log4/**,**/log_3/**,**/*.test.*,**/node_modules/**,**/dist/**,**/build/**,docker-compose.yaml" \
                  -Dsonar.coverage.exclusions="**/*.test.*,**/test/**,**/tests**"
            '''
          }
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
              --exclude '**/node_modules/**' --exclude '**/dist/**' --exclude '**/build/**' \
              --sarif -o ${SEMGREP_SARIF} \
              --junit-xml --junit-xml-file ${SEMGREP_JUNIT} \
              --severity error --error
        """
      }
      post {
        always {
          // Perlu plugin Warnings NG & JUnit di Jenkins
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
