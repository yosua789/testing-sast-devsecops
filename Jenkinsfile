pipeline {
  agent any

  options {
    timestamps()
  }

  environment {
    SONAR_SCANNER = 'sonar-scanner'
    SONAR_SERVER  = 'sonarqube-server'
    SEMGREP_IMAGE = 'semgrep/semgrep:latest'
    SEMGREP_SARIF = 'semgrep.sarif'
    SEMGREP_JUNIT = 'semgrep-junit.xml'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git --no-pager log -1 --pretty=oneline || true'
        sh 'ls -la'
      }
    }

    stage('SonarQube Scan') {
      steps {
        withSonarQubeEnv("${env.SONAR_SERVER}") {
          script {
            def isPR = env.CHANGE_ID?.trim()
            def sonarArgs = [
              "-Dsonar.projectKey=kecilin:testing-sast-devsecops",
              "-Dsonar.projectName=testing-sast-devsecops",
              "-Dsonar.sources=src",
              "-Dsonar.inclusions=src/**",
              "-Dsonar.exclusions=**/log/**,**/log4/**,**/log_3/**,**/*.test.*,**/node_modules/**,**/dist/**,**/build/**,docker-compose.yaml",
              "-Dsonar.coverage.exclusions=**/*.test.*,**/test/**,**/tests/**"
            ]
            if (isPR) {
              sonarArgs += [
                "-Dsonar.pullrequest.key=${env.CHANGE_ID}",
                "-Dsonar.pullrequest.branch=${env.CHANGE_BRANCH}",
                "-Dsonar.pullrequest.base=${env.CHANGE_TARGET}",
                "-Dsonar.scm.revision=${env.GIT_COMMIT}"
              ]
            } else {
              sonarArgs += ["-Dsonar.branch.name=${env.BRANCH_NAME ?: 'main'}"]
            }
            withEnv(["PATH+SONAR=${tool env.SONAR_SCANNER}/bin"]) {
              sh "sonar-scanner ${sonarArgs.join(' ')}"
            }
          }
        }
      }
    }

    stage('Quality Gate (SonarQube)') {
      when { expression { return !(env.CHANGE_ID?.trim()) } }
      steps {
        timeout(time: 15, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
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
          recordIssues(enabledForFailure: true, tools: [sarif(pattern: "${SEMGREP_SARIF}", id: 'Semgrep')])
          junit allowEmptyResults: true, testResults: "${SEMGREP_JUNIT}"
          archiveArtifacts artifacts: "${SEMGREP_SARIF}, ${SEMGREP_JUNIT}", fingerprint: true, onlyIfSuccessful: false
        }
      }
    }
  }

  post {
    always  { echo "Build result: ${currentBuild.currentResult}" }
    failure { echo "Cek temuan SonarQube & Semgrep pada halaman build." }
  }
}
