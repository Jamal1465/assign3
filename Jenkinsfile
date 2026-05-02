pipeline {
    agent any

    environment {
        // Docker image tag for the test runner
        TEST_IMAGE = "tradex-selenium-tests:${BUILD_NUMBER}"
        // GitHub repo containing THIS test code
        TEST_REPO  = "https://github.com/Bilalaaskari2003/tradex-tests.git"
        // Directory inside the workspace where tests are cloned
        TEST_DIR   = "tradex-tests"
    }

    triggers {
        // Trigger on every push via GitHub webhook
        githubPush()
    }

    stages {

        // ── Stage 1: Clone the test repository ──────────────────────
        stage('Checkout') {
            steps {
                echo 'Cloning TradeX test repository...'
                dir(TEST_DIR) {
                    git url: "${TEST_REPO}", branch: 'main'
                }
            }
        }

        // ── Stage 2: Build the test Docker image ────────────────────
        stage('Build Test Image') {
            steps {
                echo 'Building Docker image with Chrome + Selenium...'
                dir(TEST_DIR) {
                    sh "docker build -t ${TEST_IMAGE} ."
                }
            }
        }

        // ── Stage 3: Run automated Selenium tests ───────────────────
        stage('Test') {
            steps {
                echo 'Running 15 Selenium test cases in headless Chrome...'
                dir(TEST_DIR) {
                    // Run tests inside the container and copy the HTML report out.
                    // The container exits with a non-zero code if tests fail —
                    // we capture that with || true so the report is always copied
                    // before we let Jenkins decide the final build status.
                    sh """
                        docker run --rm \\
                            --name tradex-tests-${BUILD_NUMBER} \\
                            -v \$(pwd)/reports:/app/reports \\
                            ${TEST_IMAGE} \\
                            pytest tests/test_tradex.py \\
                                --html=reports/report.html \\
                                --self-contained-html \\
                                -v 2>&1 | tee reports/pytest.log; \\
                        EXIT_CODE=\${PIPESTATUS[0]}; \\
                        exit \$EXIT_CODE
                    """
                }
            }
            post {
                always {
                    // Archive test artefacts regardless of outcome
                    archiveArtifacts artifacts: "${TEST_DIR}/reports/**", allowEmptyArchive: true
                    junit allowEmptyResults: true, testResults: "${TEST_DIR}/reports/*.xml"
                }
            }
        }
    }

    // ── Post-pipeline: email results to the committer ───────────────
    post {
        always {
            script {
                // Identify who triggered the push
                def committerEmail = sh(
                    script: "git -C ${TEST_DIR} log -1 --pretty=format:'%ae'",
                    returnStdout: true
                ).trim()

                def buildStatus  = currentBuild.currentResult ?: 'UNKNOWN'
                def buildColor   = (buildStatus == 'SUCCESS') ? '#28a745' : '#dc3545'
                def reportExists = fileExists("${TEST_DIR}/reports/report.html")

                emailext(
                    subject: "[TradeX CI] Build #${BUILD_NUMBER} – ${buildStatus}",
                    to: committerEmail,
                    mimeType: 'text/html',
                    body: """
                        <html>
                        <body style="font-family: Arial, sans-serif; color: #333;">
                          <h2 style="color: ${buildColor};">
                            TradeX Selenium Tests — Build #${BUILD_NUMBER}: ${buildStatus}
                          </h2>
                          <table style="border-collapse: collapse; width: 60%;">
                            <tr>
                              <td style="padding:6px; border:1px solid #ddd;"><b>Branch</b></td>
                              <td style="padding:6px; border:1px solid #ddd;">${env.GIT_BRANCH ?: 'main'}</td>
                            </tr>
                            <tr>
                              <td style="padding:6px; border:1px solid #ddd;"><b>Commit</b></td>
                              <td style="padding:6px; border:1px solid #ddd;">${env.GIT_COMMIT ?: 'N/A'}</td>
                            </tr>
                            <tr>
                              <td style="padding:6px; border:1px solid #ddd;"><b>Build URL</b></td>
                              <td style="padding:6px; border:1px solid #ddd;">
                                <a href="${BUILD_URL}">${BUILD_URL}</a>
                              </td>
                            </tr>
                          </table>
                          <br/>
                          <p>The full HTML test report is attached below.</p>
                        </body>
                        </html>
                    """,
                    attachmentsPattern: "${TEST_DIR}/reports/report.html"
                )
            }
        }
    }
}
