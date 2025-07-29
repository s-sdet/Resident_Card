#!/bin/sh
set -e

echo "Установка зависимостей..."
pip install -r requirements.txt

echo "Запуск тестов..."
pytest tests/ \
  --testrail \
  --tr-no-ssl-cert-check \
  --tr-url="${TR_URL}" \
  --tr-email="${TR_EMAIL}" \
  --tr-password="${TR_PASSWORD}" \
  --tr-testrun-assignedto-id="${TR_TESTRUN_ASSIGNEDTO_ID}" \
  --tr-testrun-project-id="${TR_PROJECT_ID}" \
  --tr-testrun-name="${TR_TESTRUN_NAME}" \
  --tr-testrun-suite-id="${TR_TESTRUN_SUITE_ID}" \
  --tr-run-id="${TR_RUN_ID}"

echo "✅ Тесты завершены!"