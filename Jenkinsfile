pipeline {
  agent any
  options { timestamps() }

  // Gampang ganti target Sonar tanpa ubah file
  parameters {
    string(
      name: 'SONAR_HOST_URL',
      defaultValue: 'http://172.18.0.4:9000',
      description: 'URL SonarQube yang dapat diakses dari kontainer DinD (contoh: http://<IP-Sonar>:9000 atau http://<HOST-IP>:9010)'
    )
  }

  environment {
    // Kontainer dijalankan oleh DinD
    DOCKER_HOST    = 'tcp://dind:2375'

    // Semgrep
    SEMGREP_IMAGE  = 'semgrep/semgrep:latest'
    SEMGREP_SARIF  = 'semgrep.sarif'
    SEMGREP_JUNIT  = 'semgrep-junit.xml'

    // Identitas project di SonarQube
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
        sh 'echo DOCKER_HOST=$DOCKER_HOST'
        sh 'docker version'   // harus tampil Client + Server
        sh 'docker run --rm curlimages/curl -s -I "${params.SONAR_HOST_URL}" | head -n1 || true'
        sh 'docker run --rm curlimages/curl -s "${params.SONAR_HOST_URL}/api/system/status" || true'
      }
    }

    // Auto-create project kalau belum ada (butuh permission "Create Projects")
    stage('Ensure Sonar Project Exists') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
          sh '''
            set -e
            echo "Cek project ${SONAR_PROJECT_KEY}…"
            FOUND=$(docker run --rm curlimages/curl -sf -u "$SONAR_TOKEN:" \
                    "${SONAR_HOST_URL:-${params.SONAR_HOST_URL}}/api/projects/search?projects=${SONAR_PROJECT_KEY}" \
                    | grep -F "\"key\":\"${SONAR_PROJECT_KEY}\"" || true)

            if [ -z "$FOUND" ]; then
              echo "Project belum ada. Mencoba membuat…"
              docker run --rm curlimages/curl -sf -u "$SONAR_TOKEN:" -X POST \
                "${SONAR_HOST_URL:-${params.SONAR_HOST_URL}}/api/projects/create?project=${SONAR_PROJECT_KEY}&name=${SONAR_PROJECT_NAME}" \
              || { echo "GAGAL membuat project. Pastikan token punya permission 'Create Projects'."; exit 1; }
              echo "Project dibuat."
            else
              echo "Project sudah ada."
            fi
          '''
        }
      }
    }

    stage('SonarQube Scan') {
      steps {
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
          sh '''
            docker pull sonarsource/sonar-scanner-cli
            # Repo kamu tidak punya folder src/, jadi sumber = root (.)
            docker run --rm -v "$WORKSPACE:/usr/src" \
              sonarsource/sonar-scanner-cli \
                -Dsonar.host.url="${SONAR_HOST_URL:-${params.SONAR_HOST_URL}}" \
                -Dsonar.token="$SONAR_TOKEN" \
                -Dsonar.projectKey="${SONAR_PROJECT_KEY}" \
                -Dsonar.projectName="${SONAR_PROJECT_NAME}" \
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
              --exclude '**/node_modules/**' --exclude '**/dist/**' --exclude '**/build/**' \
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
    failure { echo "Cek temuan SonarQube & Semgrep di halaman build." }
  }
}
