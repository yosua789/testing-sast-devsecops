pipeline {
  agent any

  options {
    timestamps()
  }

  environment {
    // --- Sonar + Semgrep ---
    SONAR_HOST_URL = credentials('unused?') ? '' : (env.SONAR_HOST_URL ?: 'http://sonarqube:9000') // override di job
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

    stage('SonarQube Scan (Docker CLI + token credential)') {
      steps {
        withCredentials([string(credentialsId: 'sonar-qube', variable: 'SONAR_TOKEN')]) {
          sh """
            docker run --rm -v "$PWD:/usr/src" sonarsource/sonar-scanner-cli \\
              -Dsonar.host.url=${SONAR_HOST_URL} \\
              -Dsonar.login=${SONAR_TOKEN} \\
              -Dsonar.projectKey=kecilin:testing-sast-devsecops \\
              -Dsonar.projectName=testing-sast-devsecops \\
              -Dsonar.sources=src \\
              -Dsonar.inclusions=src/** \\
              -Dsonar.exclusions=**/log/**,**/log4/**,**/log_3/**,**/*.test.*,**/node_modules/**,**/dist/**,**/build/**,docker-compose.yaml \\
              -Dsonar.coverage.exclusions=**/*.test.*,**/test/**,**/tests/**
          """
        }
      }
    }

    stage('Semgrep SAST') {
      steps {
        script {
          def rules = ["p/ci", "p/owasp-top-ten", "p/docker"]
          def cfgArg = rules.collect { "--config ${it}" }.join(' ')
          sh """
            docker pull ${env.SEMGREP_IMAGE}
            docker run --rm -v "$PWD:/src" -w /src \\
              ${env.SEMGREP_IMAGE} semgrep scan \\
              ${cfgArg} \\
              --include 'src/**' \\
              --include 'DockerFile' \\
              --exclude 'log/**' --exclude 'log4/**' --exclude 'log_3/**' \\
              --sarif -o ${env.SEMGREP_SARIF} \\
              --junit-xml --junit-xml-file ${env.SEMGREP_JUNIT} \\
              --severity error --error
          """
        }
      }
      post {
        always {
          // butuh plugin Warnings NG & JUnit
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
