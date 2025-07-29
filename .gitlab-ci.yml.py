include:
  - project: 'cicd/gitlabci-templates'
    ref: dev
    file:
      - '/vault/vault-template.yml'

stages:
  - test
  - notify

autotests-mobile:
  stage: test
  image: ${REGISTRY_URL}/***/abo-abdt.ok.autotests.mobile:latest
  script:
    - ls -la
    - which sh  # Проверяем наличие sh
    - chmod +x autotests.sh
    - sh ./autotests.sh  # Запускаем через sh
  after_script:
    - echo "${CI_JOB_URL}" > job_url_mobile.txt
  artifacts:
    paths:
      - job_url_mobile.txt
    expire_in: 1 day
    when: always
  when: manual
  allow_failure: true

notify-mobile:
  stage: notify
  image: ${REGISTRY_URL}/docker/alpine/curl:latest
  needs:
    - job: autotests-mobile
      artifacts: true
  script:
    - JOB_URL=$(cat job_url_mobile.txt)
    - |
      curl -s -m3 -X POST \
      https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
      -x http://***.ru:8080 \
      -H "Content-Type: application/json" \
      -d "{\"chat_id\": \"${TELEGRAM_CHAT_ID}\", \"text\": \"Мобильные автотесты завершены, проверь результаты: ${JOB_URL}\"}"
  when: on_success
  allow_failure: true