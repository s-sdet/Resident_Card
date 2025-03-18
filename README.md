# Карта Жителя

Проект для автоматизированного тестирования Android-приложений с использованием Appium, Selenium и Python. Проект использует Page Object Model и построен с соблюдением принципов SOLID и OOP.

## Требования

- Python 3.8 и выше
- Appium Server
- Android SDK
- Устройство Android или эмулятор
- Все необходимые зависимости (см. ниже)

## Установка

1. Клонируйте репозиторий:

    ```bash
    git clone https://***/resident-card.git
    cd resident-card
    ```

2. Создайте виртуальное окружение:

    ```bash
    python -m venv venv
    ```

3. Активируйте виртуальное окружение:

    - Для Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - Для macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

4. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

5. Установите Appium и необходимые компоненты:

    - Установите [Appium](https://appium.io/) и его зависимости.
    - Убедитесь, что Android SDK и ADB настроены правильно.

## Конфигурация

Проект поддерживает конфигурацию через командную строку или переменные окружения. Аргументы передаются при запуске тестов через параметры `--device_name`, `--app_path` и `--server`.

### Аргументы командной строки

- `--device_name` — Имя устройства для тестирования. По умолчанию: `emulator-5554`.
- `--app_path` — Путь к APK файлу приложения. Если не передан, используется путь по умолчанию: `apk/***.apk`.
- `--server` — URL сервера Appium. По умолчанию: `http://localhost:4723`.

### Пример запуска теста

Для локального запуска тестов с переданными аргументами:

```bash
pytest tests/ --device_name emulator-5554 --app_path /path/to/app.apk --server http://localhost:4723
