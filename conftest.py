import os
import re
import pytest
import logging
import yaml

from pathlib import Path
from typing import Dict, Optional, Callable, Tuple, Any
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.appium_connection import AppiumConnection
from appium.webdriver.webdriver import WebDriver
from fixtures.application import Application
from api.user_api import UserAPI

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s][%(levelname)s] - %(message)s")
logger = logging.getLogger("Карта Жителя")


@pytest.fixture(scope="session")
def driver_config() -> Dict[str, str]:
    """
    Определяет источник конфигурации: локально из browserstack.yml, либо из переменных окружения.
    Возвращает словарь с device_name, server, app_path, user_name, access_key и platform_version.
    """
    is_ci = os.getenv("CI") == "true"

    if is_ci:
        # Получаем все из переменных окружения
        return {
            "device_name": os.getenv("BS_DEVICE_NAME"),
            "platform_version": os.getenv("BS_PLATFORM_VERSION"),
            "app_path": os.getenv("BS_APP_PATH"),
            "server": os.getenv("BS_SERVER_URL"),
            "user_name": os.getenv("BS_USERNAME"),
            "access_key": os.getenv("BS_ACCESS_KEY"),
        }
    else:
        # Чтение browserstack.yml
        config_path = Path(__file__).parent / "browserstack.yml"
        if not config_path.exists():
            pytest.fail("❌ Локальный файл browserstack.yml не найден")

        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        platform = config.get("platforms", [{}])[0]

        return {
            "device_name": platform.get("deviceName"),
            "platform_version": platform.get("platformVersion"),
            "app_path": config.get("app"),
            "server": f"https://{config['userName']}:{config['accessKey']}@hub-cloud.browserstack.com/wd/hub",
            "user_name": config.get("userName"),
            "access_key": config.get("accessKey"),
        }


class DriverSetup:
    def __init__(self, config: Dict[str, str], request: pytest.FixtureRequest):
        self.config = config
        self.request = request
        self.driver: Optional[WebDriver] = None

    def setup_driver(self) -> WebDriver:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = self.config["device_name"]
        options.platform_version = self.config["platform_version"]
        options.app = self.config["app_path"]
        options.automation_name = "UiAutomator2"
        options.new_command_timeout = 300
        options.auto_grant_permissions = True

        # BrowserStack capabilities
        options.set_capability("browserstack.user", self.config["user_name"])
        options.set_capability("browserstack.key", self.config["access_key"])
        options.set_capability("browserstack.local", "true")
        options.set_capability("browserstack.localIdentifier", os.getenv("BS_LOCAL_IDENTIFIER"))
        options.set_capability("project", "Citizen Card Tests")
        options.set_capability("build", "Build v1.0")
        options.set_capability("name", self.request.node.name)
        options.set_capability("browserstack.networkLogs", "true")
        options.set_capability("browserstack.debug", "true")
        options.set_capability("browserstack.appium_version", "2.0.0")
        options.set_capability("browserstack.deviceLogs", "true")

        connection = AppiumConnection(remote_server_addr=self.config["server"])
        self.driver = webdriver.Remote(command_executor=connection, options=options)
        return self.driver

    def teardown(self) -> None:
        if self.driver:
            self.driver.quit()


@pytest.fixture(scope="function", autouse=True)
def setup(request: pytest.FixtureRequest, driver_config: Dict[str, str]) -> Application:
    driver_setup = DriverSetup(driver_config, request)
    driver = driver_setup.setup_driver()
    app = Application(driver)
    if hasattr(request, "cls") and request.cls is not None:
        request.cls.app = app
    request.addfinalizer(driver_setup.teardown)
    return app


@pytest.fixture
def app(request: pytest.FixtureRequest) -> Application:
    """Фикстура для получения экземпляра приложения в тестах."""
    return request.cls.app


def parse_client_data(line: str) -> Dict[str, str]:
    """
    Извлекает данные клиента из строки в словарь.
    Args:
        line: Строка с данными клиента.
    Returns:
        Dict[str, str]: Словарь с ключами: phone, password.
    """
    pattern = re.compile(r'телефон (?P<phone>\d+), пароль (?P<password>\d+)')
    match = pattern.search(line)
    return match.groupdict() if match else {}


@pytest.fixture
def get_user_data(request: pytest.FixtureRequest) -> Callable[[bool], Tuple[str, str]]:
    """
    Фикстура для получения логина и пароля из файла с клиентскими данными.
    Args:
        request: Объект pytest для отслеживания статуса теста.
    Returns:
        Callable[[bool], Tuple[str, str]]: Функция, возвращающая кортеж (phone, password).
    """
    def _get_user_data(delete_line: bool = False) -> Tuple[str, str]:
        file_path = Path(__file__).resolve().parent / "data" / "users" / "users_list.txt"
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        if not lines:
            pytest.fail("Файл с данными пуст")
        first_line = lines[0].strip()
        parsed_data = parse_client_data(first_line)
        phone, password = parsed_data.get("phone"), parsed_data.get("password")

        if delete_line:
            def remove_used_line():
                if hasattr(request.node, "rep_call") and request.node.rep_call.passed:
                    with open(file_path, "r", encoding="utf-8") as file:
                        current_lines = file.readlines()
                    if current_lines and current_lines[0].strip() == first_line:
                        with open(file_path, "w", encoding="utf-8") as file:
                            file.writelines(current_lines[1:])
                        logger.info(f"Строка '{first_line}' удалена из {file_path} после успешного теста.")
                    else:
                        logger.warning(f"Строка '{first_line}' не найдена в файле {file_path}.")
                else:
                    logger.info(f"Тест не прошел, строка '{first_line}' не удалена.")
            request.addfinalizer(remove_used_line)
        return phone, password
    return _get_user_data


@pytest.fixture
def login_by_phone(app: Application, get_user_data: Callable[[bool], Tuple[str, str]]) -> Callable[[bool], None]:
    """
    Фикстура авторизации в приложении через банк по номеру телефона.
    Args:
        app: Экземпляр приложения.
        get_user_data: Фикстура получения данных тестового пользователя.
    Returns:
        Callable[[bool], None]: Функция для авторизации.
    """
    def _login_by_phone(delete_line: bool = False) -> None:
        phone, password = get_user_data(delete_line=delete_line)
        app.main.check_and_close_update_popup()
        app.main.assert_home_screen_is_open()
        app.main.login_via_phone(phone=phone, password=password)
    return _login_by_phone


@pytest.fixture
def issue_plastic_card(app: Application, login_by_phone: Callable[[bool], None], request: pytest.FixtureRequest) -> None:
    """
    Фикстура оформления пластиковой карты.
    Args:
        app: Экземпляр приложения.
        login_by_phone: Фикстура авторизации.
        request: Объект pytest для получения параметров.
    """
    delete_line = getattr(request, 'param', False)
    login_by_phone(delete_line=delete_line)
    app.main.check_and_close_pay_parking_popup()
    app.main.issue_card()
    app.main.issue_plastic_card()
    app.main.apply_plastic_card()


@pytest.fixture(scope="session")
def create_test_user() -> Dict[str, Any]:
    """
    Фикстура для создания тестового пользователя через API перед запуском тестов.
    Returns:
        Dict[str, Any]: Данные созданного пользователя.
    """
    return UserAPI.create_test_user()


@pytest.fixture
def user_data_selection(get_user_data: Callable[[bool], Tuple[str, str]], create_test_user: Dict[str, Any]) -> Any:
    """
    Динамическая фикстура, выбирающая источник данных в зависимости от среды.
    Args:
        get_user_data: Фикстура для локального запуска (данные из файла).
        create_test_user: Фикстура для CI/CD (создание пользователя через API).

    Returns:
        Any: Источник данных (функция или словарь).
    """
    return create_test_user if os.getenv("CI") == "true" else get_user_data


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Any:
    """
    Хук для сохранения результата выполнения теста в объект item.
    Используется для удаления данных тестового пользователя после успешного теста.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)