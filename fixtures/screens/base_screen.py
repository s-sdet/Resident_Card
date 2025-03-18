import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.pointer_input import PointerInput


class BaseScreen:
    """
    Базовый класс для работы как с нативными элементами Android-приложения, так и с WebView.
    """

    def __init__(self, driver):
        """
        Инициализация базового экрана с передачей драйвера.
        :param driver: Драйвер для взаимодействия с приложением.
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # ==== Методы работы с нативными элементами ====

    def _find_element(self, locator, wait_time=20):
        """
        Поиск элемента с ожиданием.
        :param locator: Локатор элемента.
        :param wait_time: Время ожидания.
        :return: Найденный элемент.
        """
        element = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(locator), message=f"Невозможно найти элемент по локатору: {locator}")
        return element

    def _visibility_element(self, locator, wait_time=20):
        """
        Проверка видимости элемента.
        :param locator: Локатор элемента.
        :param wait_time: Время ожидания.
        :return: Найденный элемент.
        """
        element = WebDriverWait(self.driver, wait_time).until(
            EC.visibility_of_element_located(locator), message=f"Невозможно найти элемент по локатору: {locator}")
        return element

    def element_is_enabled(self, locator, wait_time=20):
        """
        Проверка, что элемент активен.
        :param locator: Локатор элемента.
        :param wait_time: Время ожидания перед поиском элемента.
        """
        element = self._visibility_element(locator, wait_time)
        element.is_enabled()

    def click(self, locator, wait_time=20):
        """
        Клик по найденному элементу.
        :param locator: Локатор элемента.
        :param wait_time: Время ожидания перед поиском элемента.
        """
        element = self._find_element(locator, wait_time)
        element.click()

    def send_keys(self, locator, value: str, wait_time=20, delay=0):
        """
        Ввод текста в поле ввода.
        :param locator: Локатор элемента.
        :param value: Текст для ввода.
        :param wait_time: Время ожидания перед поиском элемента.
        :param delay: Время задержки между очисткой поля и вводом значения. Необходим когда поле пред заполнено каким-то
        значением и фронт возвращает его в поле после send_keys.
        """
        element = self._find_element(locator, wait_time)
        time.sleep(delay)
        element.clear()
        time.sleep(delay)
        element.send_keys(value)

    def get_text(self, locator, wait_time=20):
        """
        Получение текста из элемента.
        :param locator: Локатор элемента.
        :param wait_time: Время ожидания перед поиском элемента.
        :return: Текст элемента.
        """
        element = self._find_element(locator, wait_time)
        return element.text

    def swipe_to_refresh(self):
        """Функция для выполнения свайпа вниз для обновления экрана."""
        size = self.driver.get_window_size()
        width = size['width']
        height = size['height']
        start_x = width // 2
        start_y = int(height * 0.1)
        end_y = int(height * 0.5)

        action = ActionBuilder(self.driver, PointerInput(interaction.POINTER_TOUCH, "touch"))
        action.pointer_action.move_to_location(start_x, start_y)
        action.pointer_action.pointer_down()
        action.pointer_action.pause(0.5)
        action.pointer_action.move_to_location(start_x, end_y)
        action.pointer_action.pointer_up()
        action.perform()

    # ==== Методы работы с WebView ====

    def switch_to_webview(self):
        """
        Переключение на WebView-контекст.
        Сначала пытается переключиться на 'WEBVIEW_chrome', если он доступен.
        Если его нет, переключается на первый найденный WebView.
        """
        web_views = [context for context in self.driver.contexts if "WEBVIEW" in context]
        if not web_views:
            raise RuntimeError("WebView не найдено!")
        if "WEBVIEW_chrome" in web_views:  # Если 'WEBVIEW_chrome' есть в списке, переключаемся на него
            self.driver.switch_to.context("WEBVIEW_chrome")
        else:
            self.driver.switch_to.context(web_views[0])  # Если 'WEBVIEW_chrome' нет, переключаемся на первый доступный

    def switch_to_native(self):
        """Переключение обратно на нативный контекст приложения."""
        self.driver.switch_to.context("NATIVE_APP")

    def find_webview_element(self, locator, wait_time=20):
        element = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(locator), message=f"Невозможно найти элемент по локатору: {locator}")
        return element

    def click_webview_element(self, locator: tuple):
        """Клик по элементу в WebView."""
        element = self.find_webview_element(locator)
        element.click()

    def enter_text_in_webview(self, locator: tuple, text: str):
        """Ввод текста в поле в WebView."""
        element = self.find_webview_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text_from_webview(self, locator: tuple) -> str:
        """Получение текста из элемента WebView."""
        return self.find_webview_element(locator).text
