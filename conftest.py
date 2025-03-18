import os
import re
import pytest
import logging
import subprocess

from pathlib import Path
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.appium_connection import AppiumConnection
from fixtures.application import Application
from api.user_api import UserAPI

logger = logging.getLogger("Карта Жителя")


def pytest_addoption(parser):
    parser.addoption("--device_name", action="store", default="emulator-5554", help="Имя устройства для теста")
    parser.addoption("--app_path", action="store", default=None, help="Путь к APK файлу")
    parser.addoption("--server", action="store", default="http://localhost:4723", help="URL Appium сервера")


@pytest.fixture(scope="session")
def driver_config(request):
    """
    Фикстура для конфигурации драйвера Appium перед запуском тестов.
    Сбор конфигурационных параметров осуществляется из аргументов командной строки или переменных окружения:
    - --device_name: Имя устройства (например, эмулятор или реальное устройство).
    - --server: URL-адрес сервера Appium (например, http://127.0.0.1:4723).
    - --app_path: Путь к APK-файлу приложения (если не указан, берется из переменной окружения APP_PATH).
    - ANDROID_HOME/ANDROID_SDK_ROOT: Путь к Android SDK для работы ADB.

    Проверяется наличие необходимых файлов и переменных окружения.
    В случае отсутствия критических параметров выполнение тестов завершается с ошибкой.

    :param request: Объект запроса pytest, позволяющий получать параметры из командной строки.
    :return: Словарь с параметрами конфигурации драйвера (device_name, server, app_path).
    """

    # Получение параметров из командной строки
    device_name = request.config.getoption("--device_name")
    server = request.config.getoption("--server")

    # Путь к APK: либо из аргумента командной строки, либо из переменной окружения APP_PATH
    app_path = request.config.getoption("--app_path") or os.getenv("APP_PATH")

    # Проверка пути к Android SDK (важно для работы ADB)
    android_home = os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT")
    if not android_home:
        pytest.fail("❌ Переменные ANDROID_HOME или ANDROID_SDK_ROOT не установлены. Укажи путь к Android SDK.")

    # Если путь к APK не указан, используем APK по умолчанию в папке проекта
    if not app_path:
        project_root = os.path.dirname(os.path.abspath(__file__))  # Определение корня проекта
        app_path = os.path.join(project_root, "apk", "702-app-dev-debug.apk")  # Путь к APK по умолчанию

    app_path = os.path.abspath(app_path)  # Преобразование пути к абсолютному

    # Проверка существования APK-файла
    if not os.path.exists(app_path):
        pytest.fail(f"❌ APK-файл '{app_path}' не существует или недоступен.")

    # Возвращение конфигурации в виде словаря
    return {"device_name": device_name, "server": server, "app_path": app_path}


@pytest.fixture(scope="function", autouse=True)
def setup(request, driver_config):
    """
    Фикстура для инициализации и завершения работы драйвера Appium для Android-устройства.
    Эта фикстура будет автоматически применяться ко всем тестам.
    :param request: Экземпляр объекта запроса Pytest, необходим для получения конфигурации.
    :param driver_config: Словарь с параметрами конфигурации для драйвера (например, имя устройства, путь к APK).
    :return: Объект приложения `app` для использования в тестах.
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"  # Определяем платформу для Appium (Android)
    options.device_name = driver_config["device_name"]  # Имя устройства или идентификатор эмулятора устройства
    options.app = driver_config["app_path"]  # Путь к APK-файлу приложения, который будет устанавливаться на устройство
    options.automation_name = "UiAutomator2"  # Выбираем движок автоматизации (UiAutomator2 — стандарт для Android)
    options.no_reset = False  # Если False, приложение будет сбрасываться перед каждым запуском (удаляются данные)
    options.skip_install = False  # Если False, Appium будет заново устанавливать APK перед каждым тестом
    options.app_wait_activity = "*****, *"  # Определяем активность, на которую Appium
    # будет ждать загрузки приложения
    options.new_command_timeout = 60  # Время ожидания команд от клиента перед закрытием сессии (в секундах)
    options.app_wait_duration = 15000  # Время ожидания перед переключением на целевую активность после запуска
    options.auto_grant_permissions = True  # Автоматически предоставлять приложению все разрешения при установке
    options.ensure_webviews_have_pages = True  # Убеждаемся, что WebView полностью загружен перед началом работы с ним
    options.auto_webview = True  # Автоматически переключаться в WebView, если он обнаружен
    options.auto_webview_timeout = 10000  # Время ожидания (в миллисек) для переключения в WebView после его появления
    options.enable_automated_chromedriver_download = True  # Загрузка ChromeDriver, если версия WebView устарела

    # Определяем путь к ChromeDriver
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Папка с conftest.py
    chromedriver_path = os.path.join(base_dir, "drivers", "chromedriver", "chromedriver")
    # Добавляем расширение для Windows
    if os.name == "nt":
        chromedriver_path += ".exe"
    # Проверяем, существует ли файл chromedriver
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"ChromeDriver не найден по пути: {chromedriver_path}")
    options.chromedriver_executable = chromedriver_path

    try:
        connection = AppiumConnection(remote_server_addr=driver_config["server"])
        driver = webdriver.Remote(command_executor=connection, options=options)
    except Exception as e:
        pytest.fail(f"Не удалось запустить Appium-драйвер: {e}")

    app = Application(driver)  # Создаем экземпляр Application

    # Присваиваем app объекту класса, если он есть
    if hasattr(request, "cls") and request.cls is not None:
        request.cls.app = app

    def teardown():
        package_name = "****"
        try:
            if "browserstack" in driver.capabilities.get("platformName", "").lower():
                driver.remove_app(package_name)
                logger.info(f"Приложение {package_name} успешно удалено с устройства на BrowserStack.")
            else:
                subprocess.run(f"adb uninstall {package_name}", check=True)
                logger.info(f"Приложение {package_name} успешно удалено с устройства.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Не удалось удалить приложение {package_name} через adb. Ошибка: {e}")
        except Exception as e:
            logger.error(f"Не удалось удалить приложение {package_name}. Ошибка: {e}")
        driver.quit()
    request.addfinalizer(teardown)
    return app  # Возвращаем app напрямую для использования в тестах


@pytest.fixture
def app(request):
    """Фикстура будет использоваться в тестах для получения экземпляра приложения."""
    return request.cls.app  # Возвращаем объект, который был создан в фикстуре 'setup'


def parse_client_data(line: str) -> dict:
    """
    Извлекает данные клиента из строки в словарь.
    :param line: Строка с данными клиента.
    :return: Словарь с ключами: phone, password, login, biztalkId, crmId, way4Id.
    """
    pattern = re.compile(
        r'телефон (?P<phone>\d+), пароль (?P<password>\d+)')
    match = pattern.search(line)
    if match:
        return match.groupdict()
    return {}


@pytest.fixture
def get_user_data(request):
    """
    Фикстура для получения логина и пароля из файла с клиентскими данными data/users/users_list.txt.
    - Открывает файл с данными клиентов.
    - Берет первую строку, извлекает логин и пароль.
    - Удаляет использованную строку, если параметр delete_line=True, но только после успешного теста.
    :param request: Объект pytest для отслеживания статуса теста и добавления финализатора.
    :return: Функция, возвращающая кортеж (phone, password).
    """
    def _get_user_data(delete_line=False):
        base_dir = Path(__file__).resolve().parent  # Определяем базовую директорию
        file_path = base_dir / "data" / "users" / "users_list.txt"  # Путь к файлу с данными
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        if not lines:
            pytest.fail("Файл с данными пуст")  # Останавливаем тест, если файл пуст
        first_line = lines[0].strip()
        parsed_data = parse_client_data(first_line)
        phone, password = parsed_data.get("phone"), parsed_data.get("password")

        # Финализатор для удаления строки тестового пользователя после выпуска карты на его данные
        if delete_line:
            def remove_used_line():
                # Проверяем статус теста
                if hasattr(request.node, "rep_call") and request.node.rep_call.passed:
                    # Перечитываем файл, чтобы убедиться в актуальности данных
                    with open(file_path, "r", encoding="utf-8") as file:
                        current_lines = file.readlines()
                    if current_lines and current_lines[0].strip() == first_line:
                        with open(file_path, "w", encoding="utf-8") as file:
                            file.writelines(current_lines[1:])  # Удаляем первую строку
                        logger.info(f"Строка '{first_line}' удалена из {file_path} после успешного теста.")
                    else:
                        logger.warning(
                            f"Строка '{first_line}' не найдена в файле {file_path}, возможно, файл был изменен.")
                else:
                    logger.info(f"Тест не прошел, строка '{first_line}' не удалена.")
            # Добавляем финализатор для удаления строки после теста
            request.addfinalizer(remove_used_line)
        return phone, password
    return _get_user_data


@pytest.fixture
def login_by_phone(app, get_user_data):
    """
    Фикстура авторизации в приложении через банк по номеру телефона.
    :param get_user_data: Фикстура полученния данных тестового пользвателя из data/users/users_list.txt
    """
    def _login_by_phone(delete_line=False):
        phone, password = get_user_data(delete_line=delete_line)
        app.main.check_and_close_update_popup()
        app.main.assert_home_screen_is_open()
        app.main.login_via_phone(phone=phone, password=password)
    return _login_by_phone


@pytest.fixture
def issue_plastic_card(app, login_by_phone, request):
    """
    Фикстура оформления пластиковой карты.
    :param login_by_phone: Фикстура авторизации в КЖ через АБОЛ.
    :param request: Объект pytest для отслеживания статуса теста.
    """
    delete_line = getattr(request, 'param', False)  # Получаем параметр delete_line, если передан
    login_by_phone(delete_line=delete_line)
    app.main.check_and_close_pay_parking_popup()
    app.main.issue_card()
    app.main.issue_plastic_card()
    app.main.apply_plastic_card()


@pytest.fixture(scope="session")
def create_test_user():
    """
    Фикстура для создания тестового пользователя через API перед запуском тестов.
    Запускается один раз за сессию и передает данные в тест.
    """
    user_data = UserAPI.create_test_user()
    return user_data


@pytest.fixture
def user_data_selection(get_user_data, create_test_user):
    """
    Динамическая фикстура, выбирающая источник данных взависимости от того где запускаются тесты:
    :param get_user_data: берет данные из 'data/users/users_list.txt' если тест запущен локально
    :param create_test_user: создает пользователя, если тест запущен в CI/CD
    """
    if os.getenv("CI") == "true":
        return create_test_user
    return get_user_data


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук для сохранения результата выполнения теста в объект item.
    Нужен для для удаления данных тестового пользователя только после успешного прохождения тестов на выпуск карты.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)