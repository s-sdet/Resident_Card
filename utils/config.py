import os


def get_config():
    """
    Функция для получения конфигурации из переменных окружения. Эти параметры могут быть использованы
    для настройки устройства, APK файла и других данных, связанных с запуском тестов.
    """
    return {
        "APPIUM_SERVER": os.getenv("APPIUM_SERVER", "http://localhost:4723"),
        "DEVICE_NAME": os.getenv("DEVICE_NAME", "emulator-5554"),
        "APP_PATH": os.getenv("APP_PATH", "apk/app-debug.apk"),
    }
