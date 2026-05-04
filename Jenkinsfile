pipeline {
    agent any

    environment {
        TEST_IMAGE = "tradex-selenium-tests:${BUILD_NUMBER}"
        TEST_REPO  = "https://github.com/Bilalaaskari2003/tradex-tests.git"
        TEST_DIR   = "tradex-tests"
        APP_URL    = "http://3.222.182.127:3000"
        API_URL    = "http://3.222.182.127:8000"
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Cloning TradeX test repository...'
                dir(TEST_DIR) {
                    git url: "${TEST_REPO}", branch: 'main'
                }
            }
        }

        stage('Build Test Image') {
            steps {
                echo 'Building Docker image with Chrome + Selenium...'
                dir(TEST_DIR) {
                    sh "docker build -t ${TEST_IMAGE} ."
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Bringing TradeX application up...'
                sh """
                    cd ~/Assign2/TradeX
                    docker compose up -d
                    sleep 10
                """
            }
        }

        stage('Test') {
            steps {
                echo 'Running 15 Selenium test cases in headless Chrome...'
                dir(TEST_DIR) {
                    sh """
                        mkdir -p \$(pwd)/reports
                        chmod 777 \$(pwd)/reports

                        docker run --rm \\
                            --name tradex-tests-${BUILD_NUMBER} \\
                            -e BASE_URL=${APP_URL} \\
                            -v \$(pwd)/reports:/app/reports \\
                            ${TEST_IMAGE} \\
                            pytest tests/test_tradex.py \\
                                --html=reports/report.html \\
                                --self-contained-html \\
                                --junitxml=reports/results.xml \\
                                -v
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${TEST_DIR}/reports/**",
                                     allowEmptyArchive: true
                    junit allowEmptyResults: true,
                          testResults: "${TEST_DIR}/reports/results.xml"
                }
            }
        }
    }

    post {
        always {
            script {

                // 1. Get committer email
                def committerEmail = "admin@example.com"
                try {
                    committerEmail = sh(
                        script: "cd ${TEST_DIR} && git log -1 --pretty=format:'%ae'",
                        returnStdout: true
                    ).trim()
                    echo "Sending results to: ${committerEmail}"
                } catch (Exception e) {
                    echo "Could not get committer email, using default."
                }

                // 2. Build status and color
                def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'
                def buildColor  = (buildStatus == 'SUCCESS') ? '#28a745' : '#dc3545'
                def statusIcon  = (buildStatus == 'SUCCESS') ? '✅' : '❌'

                // 3. Parse test summary from JUnit XML
                def testSummary = "Report not available"
                def xmlPath     = "${TEST_DIR}/reports/results.xml"

                if (fileExists(xmlPath)) {
                    def xml    = readFile(xmlPath)
                    def tm     = (xml =~ /tests="(\d+)"/)
                    def fm     = (xml =~ /failures="(\d+)"/)
                    def em     = (xml =~ /errors="(\d+)"/)
                    def total  = tm.find() ? tm.group(1) : "0"
                    def failed = fm.find() ? fm.group(1) : "0"
                    def errors = em.find() ? em.group(1) : "0"
                    def passed = (total.toInteger() - failed.toInteger() - errors.toInteger()).toString()
                    testSummary = "${passed} passed, ${failed} failed, ${errors} errors (total: ${total})"
                }

                // 4. Clean branch name
                def branchName = (env.GIT_BRANCH ?: 'main').replaceAll('origin/', '')

                // 5. Send email
                emailext(
                    subject: "[TradeX CI] Build #${BUILD_NUMBER} — ${statusIcon} ${buildStatus}",
                    to: committerEmail,
                    mimeType: 'text/html',
                    body: """
                        <html>
                        <body style="font-family:'Segoe UI',Tahoma,sans-serif; padding:20px; color:#333;">
                          <div style="
                            border-top: 8px solid ${buildColor};
                            background: #f9f9f9;
                            padding: 24px;
                            border-radius: 6px;
                            max-width: 620px;
                            margin: auto;
                            border: 1px solid #ddd;">

                            <h2 style="color:${buildColor}; margin-top:0;">
                              ${statusIcon} TradeX Selenium Tests — Build #${BUILD_NUMBER}: ${buildStatus}
                            </h2>

                            <p>The automated Selenium test pipeline has completed. Here is the summary:</p>

                            <table style="width:100%; border-collapse:collapse; background:white; border:1px solid #eee; border-radius:4px;">
                              <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:10px; font-weight:bold; width:40%;">📊 Test Results</td>
                                <td style="padding:10px;">${testSummary}</td>
                              </tr>
                              <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:10px; font-weight:bold;">🌿 Branch</td>
                                <td style="padding:10px;">${branchName}</td>
                              </tr>
                              <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:10px; font-weight:bold;">🔢 Build Number</td>
                                <td style="padding:10px;">#${BUILD_NUMBER}</td>
                              </tr>
                              <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:10px; font-weight:bold;">🌐 Frontend URL</td>
                                <td style="padding:10px;"><a href="${APP_URL}">${APP_URL}</a></td>
                              </tr>
                              <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:10px; font-weight:bold;">⚙️ Backend API</td>
                                <td style="padding:10px;"><a href="${API_URL}/docs">${API_URL}/docs</a></td>
                              </tr>
                              <tr>
                                <td style="padding:10px; font-weight:bold;">🔗 Jenkins Build</td>
                                <td style="padding:10px;"><a href="${BUILD_URL}">${BUILD_URL}</a></td>
                              </tr>
                            </table>

                            <p style="margin-top:20px;">
                              The full HTML test report is <b>attached</b> to this email.
                            </p>

                            <hr style="border:0; border-top:1px solid #eee; margin:20px 0;" />
                            <p style="font-size:11px; color:#888; text-align:center;">
                              TradeX CI/CD System &bull; Automated DevOps Pipeline
                            </p>
                          </div>
                        </body>
                        </html>
                    """,
                    attachmentsPattern: "${TEST_DIR}/reports/report.html"
                )

                echo "Email sent to ${committerEmail}"
            }
        }
    }
}
