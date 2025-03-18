import time
import logging

from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.keys import Keys
from selenium.common import NoSuchElementException, TimeoutException
from fixtures.screens.base_screen import BaseScreen
from selenium.webdriver.common.action_chains import ActionChains
from helper.otp_provider_helper import OTPRequestHelper
from data.constants import MainScreenNotice as Notice

logger = logging.getLogger("Карта Жителя")


class MainScreen(BaseScreen):
    """
    Главный экран приложения. Этот класс содержит действия для взаимодействия с элементами главного экрана,
    такими как кнопка выпуска новой карты и авторизация через АБОЛ.
    """
    # Локаторы текстов
    TEXT_UPDATE_APP = (AppiumBy.XPATH, '//android.widget.TextView[@text="Обновите приложение"]')
    TEXT_SKIP = (By.XPATH, "//p[contains(text(), 'Пропустить')]")
    TEXT_ADD_CODE = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:id/titleView"]')
    TEXT_PAY_PARKING = (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Оплата парковок")]')
    TEXT_ISSUE_CARD = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:id/text"]')
    TEXT_ORDER_RESIDENT_CARD = (
        AppiumBy.XPATH,
        '//android.widget.TextView[@resource-id="*****:id/tv_header_choose_card_type"]')
    TEXT_APPLY_CARD = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:id/text"]')
    TEXT_CARD_ISSUANCE = (AppiumBy.XPATH, '//android.widget.TextView[@text="Выдача карты"]')
    TEXT_CITY_IN_LIST = (
        AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:id/tv_main_row_item"]')
    TEXT_NEXT_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:id/text"]')
    TEXT_RECEIPT = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                    'id/kit_title_check_box"]')
    TEXT_ADDRESS_TO_RECEIVE_CARD = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                                    'id/kit_label_large_button" and @text="Адрес"]')
    TEXT_ADDRESS_OF_BANK_BRANCH = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                                   'id/kit_label_large_button" and @text="Отделение получения"]')
    TEXT_SELECT_BANK_BRANCH = (AppiumBy.XPATH, '//android.widget.TextView[@text="Выбор отделения"]')
    TEXT_UNIFIED_REFERENCE_SERVICE = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="ru.akbars.citizencard.'
                                                      'dev:id/kit_tv_label_description"]')
    TEXT_DELIVERY_STREET = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                            'id/tv_main_row_item" and contains(@text, "ул")]')
    TEXT_CARD_ORDERED = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                         'id/tv_title_result"]')
    TEXT_REQUEST_IS_PROCESSED = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                                 'id/tv_header_row_finances"]')
    TEXT_CARD_RESIDENT_TATARSTAN = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                                    'id/tv_subheader_row_finances"]')

    # Уведомления
    NOTICE_CANNOT_DELIVERED_CARD = (
        AppiumBy.XPATH, '//android.widget.TextView[@text="Мы не можем доставить карту в это место. '
                        'Попробуйте ввести другой запрос"]')

    # Кнопки
    BUTTON_CLOSE = (
        AppiumBy.XPATH, '//androidx.compose.ui.platform.ComposeView/android.view.View/android.widget.Button')
    BUTTON_LOGIN_VIA_AK_BARS = (AppiumBy.XPATH, '//android.widget.TextView[@text="Войти через Ак Барс Банк"]')
    BUTTON_LOGIN = (By.XPATH, "//button[@id='submit-button']")
    BUTTON_1 = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:id/bt_1"]')
    BUTTON_BY_COURIER = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                         'id/tv_check_box" and @text="Курьером"]')
    BUTTON_BY_BANK = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:'
                                      'id/tv_check_box" and @text="В отделении"]')
    BUTTON_SELECT_ADDRESS = (AppiumBy.XPATH, '(//android.widget.TextView[@resource-id="*****:'
                                             'id/tv_large_button"])[2]')
    BUTTON_CONFIRM = (AppiumBy.XPATH, '//android.view.ViewGroup[@resource-id="*****:'
                                      'id/cl_main_kit_progress_button"]')

    # Ссылки
    LINK_ISSUE_PLASTIC_CARD = (
        AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="*****:'
                        'id/btn_plastic_card_type"]/android.view.ViewGroup')
    LINK_CITY_IN_LIST = (
        AppiumBy.XPATH, '//androidx.recyclerview.widget.RecyclerView[@resource-id="*****:id/list"]'
                        '/android.widget.FrameLayout/android.widget.LinearLayout')
    LINK_SELECT_FIRST_BANK_BRANCH = (
        AppiumBy.XPATH, '//androidx.recyclerview.widget.RecyclerView[@resource-id="*****:'
                        'id/list"]/android.widget.FrameLayout[1]/android.widget.LinearLayout')

    # Вкладки
    LOGIN_BY_PASSWORD = (By.XPATH, "//label[@id='password-btn']")

    # Поля ввода
    FIELD_PASSWORD = (By.XPATH, "//input[@id='input-password']")
    FIELD_CITY = (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="android:id/edit"]')
    FIELD_CITY_RECEIPT = (
        AppiumBy.XPATH, '//android.widget.TextView[@resource-id="*****:id/tv_large_button"]')

    # Попапы
    POPUP_BANK_BRANCH = (AppiumBy.XPATH, '//android.widget.FrameLayout[@resource-id="*****:'
                                         'id/design_bottom_sheet"]/android.widget.LinearLayout')

    def check_and_close_update_popup(self):
        """Метод проверки появления и закрытия WebView и нативных попапов."""
        try:
            logger.info("Ищем окно обновления приложения.")
            update_popup = self._find_element(locator=self.TEXT_UPDATE_APP)
            if update_popup:
                logger.info("Найдено окно обновления приложения, закрываем его.")
                self.click(locator=self.BUTTON_CLOSE)
                logger.info("Окно обновления приложения закрыто, продолжаем тест.")
                return  # Попап найден и закрыт, продолжаем тест

        except (NoSuchElementException, TimeoutException):
            logger.info("Окно обновления приложения не найдено. Пытаемся закрыть WebView.")

        # Если TEXT_UPDATE_APP не найден, пробуем закрыть WebView кнопкой "назад"
        try:
            self.driver.press_keycode(4)  # Android keycode "назад"
            logger.info("Нажали кнопку 'назад' для выхода из WebView.")
        except Exception as e:
            logger.warning(f"Ошибка при попытке закрытия WebView: {e}")

        # Повторно проверяем наличие попапа
        try:
            logger.info("Повторно ищем окно обновления приложения после закрытия WebView.")
            update_popup = self._find_element(locator=self.TEXT_UPDATE_APP)
            if update_popup:
                logger.info("Найдено окно обновления приложения после закрытия WebView. Закрываем его.")
                self.click(locator=self.BUTTON_CLOSE)
                logger.info("Окно обновления приложения закрыто, продолжаем тест.")
            else:
                logger.info("Окно обновления приложения не найдено после закрытия WebView. Продолжаем тест.")

        except (NoSuchElementException, TimeoutException):
            logger.info("Окно обновления приложения не найдено после попытки закрыть WebView. Продолжаем тест.")

    def assert_home_screen_is_open(self):
        """Проверка, что открыт главный экран приложения и кнопка 'Войти через Ак Барс Банк' доступна."""
        button = self.get_text(locator=self.BUTTON_LOGIN_VIA_AK_BARS)
        logger.info(f"Кнопка авторизации '{button}' найдена")

    def login_via_phone(self, phone: str = "123456789", password: str = "123456789", delay=4):
        """
        Авторизация в приложении через Ак Барс Банк по номеру телефона и кодом подтверждения.
        :param phone: Номер моб телефона тестового пользователя
        :param password: Пароль тестового пользователя, у всех одинаковый: 123456789
        """
        self.element_is_enabled(locator=self.BUTTON_LOGIN_VIA_AK_BARS)  # Ожидание элемента
        self.click(locator=self.BUTTON_LOGIN_VIA_AK_BARS)
        actions = ActionChains(self.driver)
        time.sleep(delay)
        for char in phone:
            actions.send_keys(char).perform()
            time.sleep(0.1)  # Задержка т.к. эмулятор обрабатывает быстрый ввод как один блок и пропускает символы
        actions.send_keys(Keys.ENTER).perform()  # Имитация нажатия Enter

        otp_helper = OTPRequestHelper(phone=phone)
        otp_code = otp_helper.get_notifications().get_login_code()  # Получаем код подтверждения из API
        actions.send_keys(otp_code).perform()  # Вставляем полученный код

        self.switch_to_webview()  # Переключаемся с native на webview
        self.element_is_enabled(locator=self.LOGIN_BY_PASSWORD)  # Ожидание элемента
        logger.info(f"Вкладка '{self.get_text(locator=self.LOGIN_BY_PASSWORD)}' найдена.")
        assert self.get_text(locator=self.LOGIN_BY_PASSWORD) == "По паролю"
        self.click(locator=self.LOGIN_BY_PASSWORD)  # Переключаемся на вкладку "По паролю"
        self.element_is_enabled(locator=self.FIELD_PASSWORD)  # Ожидание элемента
        self.send_keys(locator=self.FIELD_PASSWORD, value=password)  # Ввод пароля
        actions.send_keys(Keys.ENTER).perform()  # Имитация нажатия Enter

        self.switch_to_native()  # Переключаемся с webview на native
        self.element_is_enabled(locator=self.TEXT_ADD_CODE)  # Ожидание элемента
        logger.info(f"Открыт экран '{self.get_text(locator=self.TEXT_ADD_CODE)}'")
        assert "Установите" in self.get_text(locator=self.TEXT_ADD_CODE)
        [self.click(locator=self.BUTTON_1) for _ in range(4)]  # Вводим код приложения: 1111
        self.element_is_enabled(locator=self.TEXT_ADD_CODE)  # Ожидание элемента
        logger.info(f"Открыт экран '{self.get_text(locator=self.TEXT_ADD_CODE)}'")
        assert self.get_text(locator=self.TEXT_ADD_CODE) == "Повторите код"
        [self.click(locator=self.BUTTON_1) for _ in range(4)]  # Повторный ввод кода приложения: 1111

    def check_and_close_pay_parking_popup(self):
        """Метод проверки появления и закрытия popup 'Оплата парковок в Карте жителя'."""
        try:
            logger.info("Ищем popup 'Оплата парковок в Карте жителя'.")
            pay_parking_popup = self._find_element(locator=self.TEXT_PAY_PARKING)
            if pay_parking_popup:
                self.click(locator=self.BUTTON_CLOSE)
                logger.info("Popup 'Оплата парковок в Карте жителя' закрыт.")
        except (NoSuchElementException, TimeoutException):
            logger.info("Popup 'Оплата парковок в Карте жителя' не найден. Продолжаем тест.")

    def issue_card(self):
        """Метод перехода к выпуску карты с главного экрана приложения."""
        self.element_is_enabled(locator=self.TEXT_ISSUE_CARD)  # Ожидание элемента
        logger.info(f"Кнопка '{self.get_text(locator=self.TEXT_ISSUE_CARD)}' найдена.")
        assert self.get_text(locator=self.TEXT_ISSUE_CARD) == "Выпустить карту"
        self.click(locator=self.BUTTON_CONFIRM)  # Клик 'Выпустить карту'

    def issue_plastic_card(self):
        """Метод выпуска пластиковой карты."""
        self.element_is_enabled(locator=self.TEXT_ORDER_RESIDENT_CARD)  # Ожидание элемента
        logger.info(f"Popup '{self.get_text(locator=self.TEXT_ORDER_RESIDENT_CARD)}' открылся.")
        self.element_is_enabled(locator=self.LINK_ISSUE_PLASTIC_CARD)  # Ожидание элемента
        self.click(locator=self.LINK_ISSUE_PLASTIC_CARD)  # Клик выпуска пластиковой карты

    def issue_digital_card(self):
        """Метод выпуска виртуальной карты."""
        self.element_is_enabled(locator=self.TEXT_ORDER_RESIDENT_CARD)  # Ожидание элемента
        logger.info(f"Popup '{self.get_text(locator=self.TEXT_ORDER_RESIDENT_CARD)}' открылся.")
        self.element_is_enabled(locator=self.LINK_ISSUE_PLASTIC_CARD)  # Ожидание элемента
        self.click(locator=self.LINK_ISSUE_PLASTIC_CARD)  # Клик выпуска пластиковой карты

    def apply_plastic_card(self):
        """Метод оформления пластиковой карты."""
        self.element_is_enabled(locator=self.TEXT_APPLY_CARD)  # Ожидание элемента
        logger.info(f"Кнопка '{self.get_text(locator=self.TEXT_APPLY_CARD)}' найдена.")
        assert self.get_text(locator=self.TEXT_APPLY_CARD) == "Оформить карту"
        self.click(locator=self.BUTTON_CONFIRM)  # Клик 'Оформить карту'
        assert self.get_text(locator=self.TEXT_CARD_ISSUANCE) == "Выдача карты"

    def input_delivery_city(self, city: str = "Альметьевск"):
        """
        Ввод города доставки пластиковой карты.
        :param city: Город выдачи карты
        """
        assert self.get_text(locator=self.TEXT_CARD_ISSUANCE) == "Выдача карты"
        logger.info(f"Открыт экран: {self.get_text(locator=self.TEXT_CARD_ISSUANCE)}")
        self.send_keys(locator=self.FIELD_CITY, value=city, delay=2)
        self.element_is_enabled(locator=self.TEXT_CITY_IN_LIST)  # Ожидание элемента
        assert city in self.get_text(locator=self.TEXT_CITY_IN_LIST)

    def input_delivery_invalid_city(self, city: str = "Нальчик", notice: str = Notice.NOTICE_CANNOT_DELIVERED_CARD):
        """
        Ввод невалидного города доставки пластиковой карты.
        :param city: Город выдачи карты
        :param notice: Текст уведомления
        """
        assert self.get_text(locator=self.TEXT_CARD_ISSUANCE) == "Выдача карты"
        logger.info(f"Открыт экран: {self.get_text(locator=self.TEXT_CARD_ISSUANCE)}")
        self.send_keys(locator=self.FIELD_CITY, value=city)
        assert notice == self.get_text(locator=self.NOTICE_CANNOT_DELIVERED_CARD)

    def select_delivery_option(self, notice: str = "Получение"):
        """
        Выбор способа доставки пластиковой карты.
        :param notice: Текст уведомления
        """
        self.click(locator=self.LINK_CITY_IN_LIST)
        assert self.get_text(locator=self.TEXT_NEXT_BUTTON) == "Далее"
        self.click(locator=self.BUTTON_CONFIRM)
        assert self.get_text(locator=self.TEXT_RECEIPT) == notice

    def receive_card_by_courier(self, notice: str = "Получение"):
        """
        Выбор варианта получения карты курьером.
        :param notice: Текст уведомления "Получение"
        """
        self.click(locator=self.LINK_CITY_IN_LIST)
        assert self.get_text(locator=self.TEXT_NEXT_BUTTON) == "Далее"
        self.click(locator=self.BUTTON_CONFIRM)
        assert self.get_text(locator=self.TEXT_RECEIPT) == notice
        self.element_is_enabled(locator=self.BUTTON_BY_COURIER)  # Ожидание элемента
        self.click(locator=self.BUTTON_BY_COURIER)  # Выбор варианта доставки "Курьером"
        self.element_is_enabled(locator=self.TEXT_ADDRESS_TO_RECEIVE_CARD)  # Ожидание элемента
        logger.info(f"Появилось поле: {self.get_text(locator=self.TEXT_ADDRESS_TO_RECEIVE_CARD)}")
        assert self.get_text(locator=self.TEXT_ADDRESS_TO_RECEIVE_CARD) == Notice.NOTICE_ADDRESS_TO_RECEIVE_CARD

    def receive_card_from_bank(self, notice: str = "Получение"):
        """
        Выбор варианта получения карты в отделении банка.
        :param notice: Текст уведомления "Получение"
        """
        self.click(locator=self.LINK_CITY_IN_LIST)
        assert self.get_text(locator=self.TEXT_NEXT_BUTTON) == "Далее"
        self.click(locator=self.BUTTON_CONFIRM)
        assert self.get_text(locator=self.TEXT_RECEIPT) == notice
        self.element_is_enabled(locator=self.BUTTON_BY_BANK)  # Ожидание элемента
        self.click(locator=self.BUTTON_BY_BANK)  # Выбор варианта доставки "В отделении"
        self.element_is_enabled(locator=self.TEXT_ADDRESS_OF_BANK_BRANCH)  # Ожидание элемента
        logger.info(f"Появилось поле: {self.get_text(locator=self.TEXT_ADDRESS_OF_BANK_BRANCH)}")
        assert self.get_text(locator=self.TEXT_ADDRESS_OF_BANK_BRANCH) == Notice.NOTICE_ADDRESS_OF_BANK_BRANCH

    def how_to_get_card(self, method: str):
        """
        Выбор способа получения карты.
        :param method: Способ получения карты (передается из теста)
        """
        if method == "bank":
            self.receive_card_from_bank()
        elif method == "courier":
            self.receive_card_by_courier()
        else:
            raise ValueError(f"Неизвестный способ получения карты: {method}")

    def select_branch_to_receive_card(self):
        """Выбор отделения банка для получения пластиковой карты."""
        # Открываем список доступных отделений банка
        self.element_is_enabled(locator=self.BUTTON_SELECT_ADDRESS)  # Ожидание элемента
        self.click(locator=self.BUTTON_SELECT_ADDRESS)  # Открыть список адресов
        self.element_is_enabled(locator=self.TEXT_SELECT_BANK_BRANCH)  # Ожидание элемента
        logger.info(f"Открылся экран: {self.get_text(locator=self.TEXT_SELECT_BANK_BRANCH)}")
        assert self.get_text(locator=self.TEXT_SELECT_BANK_BRANCH) == Notice.TEXT_SELECT_BANK_BRANCH

        # Выбираем в списке первое отделение банка
        self.click(locator=self.LINK_SELECT_FIRST_BANK_BRANCH)  # Выбрать первое отделение банка в списке
        self.element_is_enabled(locator=self.TEXT_UNIFIED_REFERENCE_SERVICE)  # Ожидание элемента
        logger.info(f"Открылся попап с: {self.get_text(locator=self.TEXT_UNIFIED_REFERENCE_SERVICE)}")
        self.click(locator=self.BUTTON_CONFIRM)  # Подтверждение выбора отделения банка

        # Проверяем, что после выбора отделения банка мы вернулись на экран вариантов доставки карты
        self.element_is_enabled(locator=self.TEXT_ADDRESS_OF_BANK_BRANCH)  # Ожидание элемента
        logger.info(f"Появилось поле: {self.get_text(locator=self.TEXT_ADDRESS_OF_BANK_BRANCH)}")
        assert self.get_text(locator=self.TEXT_ADDRESS_OF_BANK_BRANCH) == Notice.NOTICE_ADDRESS_OF_BANK_BRANCH
        self.element_is_enabled(locator=self.BUTTON_CONFIRM)  # Ожидание элемента

    def open_page_to_input_address(self):
        """Открытие страницы для ввода адреса доставки карты курьером."""
        # Открываем поле для ввода адреса доставки
        self.element_is_enabled(locator=self.BUTTON_SELECT_ADDRESS)  # Ожидание элемента
        self.click(locator=self.BUTTON_SELECT_ADDRESS)  # Открыть форму ввода адреса

        # Проверяем, что открылась нужная страница и есть поле ввода адреса доставки
        self.element_is_enabled(locator=self.TEXT_CARD_ISSUANCE)  # Ожидание элемента
        logger.info(f"Открылась страница: {self.get_text(locator=self.TEXT_CARD_ISSUANCE)}")
        assert self.get_text(locator=self.TEXT_CARD_ISSUANCE) == Notice.TEXT_CARD_ISSUANCE
        self.element_is_enabled(locator=self.FIELD_CITY)  # Проверяем появление поля ввода адреса

    def courier_delivery_change_city(self, city: str = "Казань"):
        """
        Смена города после выбора доставки карты курьером.
        :param city: Новый город доставки карты
        """
        self.click(locator=self.FIELD_CITY_RECEIPT)  # Клик по полю "Город, где вы хотите получить карту"
        # Возвращаемся на страницу ввода города доставки карты
        assert self.get_text(locator=self.TEXT_CARD_ISSUANCE) == "Выдача карты"
        logger.info(f"Открыт экран: {self.get_text(locator=self.TEXT_CARD_ISSUANCE)}")
        self.send_keys(locator=self.FIELD_CITY, value=city, delay=3)  # Вводим новый город в поле
        self.element_is_enabled(locator=self.TEXT_CITY_IN_LIST)  # Ожидание элемента
        assert city in self.get_text(locator=self.TEXT_CITY_IN_LIST)  # Проверяем, что город появился в списке
        self.click(locator=self.LINK_CITY_IN_LIST)  # Выбираем город из списка
        assert self.get_text(locator=self.TEXT_NEXT_BUTTON) == Notice.TEXT_NEXT
        self.click(locator=self.BUTTON_CONFIRM)
        logger.info(f"Город доставки: {self.get_text(locator=self.FIELD_CITY_RECEIPT)}")
        assert city in self.get_text(locator=self.FIELD_CITY_RECEIPT)  # Проверяем, что отображается новый город
        assert self.get_text(locator=self.TEXT_RECEIPT) == Notice.TEXT_RECEIPT  # Проверяем варианты доставки
        self.element_is_enabled(locator=self.BUTTON_CONFIRM)  # Проверяем, что кнопка "Заказать" отображается

    def validate_input_delivery_valid_address(self, street: str = "Чистопольская, д 1"):
        """Валидация ввода адреса доставки пластиковой карты курьерской службой."""
        self.send_keys(locator=self.FIELD_CITY, value=street[:5])  # Вводим часть улицы для валидации подсказки
        assert street[:5] in self.get_text(locator=self.TEXT_DELIVERY_STREET)
        logger.info(f"Название улицы после частичного ввода адреса: {self.get_text(locator=self.TEXT_DELIVERY_STREET)}")
        self.send_keys(locator=self.FIELD_CITY, value=street)  # Вводим название улицы полностью
        assert street in self.get_text(locator=self.TEXT_DELIVERY_STREET)
        logger.info(f"Название улицы после полного ввода адреса: {self.get_text(locator=self.TEXT_DELIVERY_STREET)}")
        self.click(locator=self.TEXT_DELIVERY_STREET)  # Кликом выбираем первый адрес из фильтра
        self.element_is_enabled(locator=self.BUTTON_CONFIRM)  # Проверяем, что кнопка "Заказать" отображается

    def validate_input_delivery_invalid_address(
            self, street: str = "Чистопольская", invalid_street: str = "Федора Абрамова"):
        """Валидация ввода невалидного адреса доставки пластиковой карты курьерской службой."""
        self.send_keys(locator=self.FIELD_CITY, value=street[:5])  # Вводим часть улицы для валидации подсказки
        assert street[:5] in self.get_text(locator=self.TEXT_DELIVERY_STREET)
        logger.info(f"Название улицы после частичного ввода адреса: {self.get_text(locator=self.TEXT_DELIVERY_STREET)}")
        self.send_keys(locator=self.FIELD_CITY, value=invalid_street)  # Вводим невалидное название улицы
        assert self.get_text(locator=self.NOTICE_CANNOT_DELIVERED_CARD) == Notice.NOTICE_CANNOT_DELIVERED_CARD

    def validate_input_delivery_address(self, method: str):
        """
        Выбор метода валидации ввода адреса доставки карты.
        :param method: Метод ввода адреса (передается из теста)
        """
        if method == "valid":
            self.validate_input_delivery_valid_address()
        elif method == "invalid":
            self.validate_input_delivery_invalid_address()
        else:
            raise ValueError(f"Неизвестный адрес доставки карты: {method}")

    def input_delivery_address(self, street: str = "Чистопольская, д 1"):
        """Ввод адреса доставки пластиковой карты курьерской службой."""
        self.send_keys(locator=self.FIELD_CITY, value=street)  # Вводим название улицы полностью
        assert street in self.get_text(locator=self.TEXT_DELIVERY_STREET)
        logger.info(f"Введено название улицы: {self.get_text(locator=self.TEXT_DELIVERY_STREET)}")
        self.click(locator=self.TEXT_DELIVERY_STREET)  # Кликом выбираем первый адрес из фильтра
        self.element_is_enabled(locator=self.BUTTON_CONFIRM)  # Проверяем, что кнопка "Заказать" отображается

    def confirm_delivery_address(self):
        """Подтверждаем выбор адреса."""
        self.element_is_enabled(locator=self.BUTTON_CONFIRM)  # Проверяем, что кнопка "Заказать" отображается
        self.click(locator=self.BUTTON_CONFIRM)  # Подтверждаем выбор адреса

    def order_card(self):
        """Метод заказа карты."""
        self.click(locator=self.BUTTON_CONFIRM)  # Заказываем карту
        logger.info(f"Статус заказа карты: {self.get_text(locator=self.TEXT_CARD_ORDERED)}")
        assert self.get_text(locator=self.TEXT_CARD_ORDERED) == Notice.TEXT_CARD_ORDERED

    def return_to_home_screen(self):
        """Возврат на главный экран после заказа карты."""
        self.element_is_enabled(locator=self.BUTTON_CONFIRM)  # Ожидание элемента
        self.click(locator=self.BUTTON_CONFIRM)  # Возвращаемся на главный экран
        self.swipe_to_refresh()
        self.element_is_enabled(locator=self.TEXT_REQUEST_IS_PROCESSED)  # Ожидание элемента
        logger.info(f"На главном экране отображается: {self.get_text(locator=self.TEXT_CARD_RESIDENT_TATARSTAN)}")
        assert self.get_text(locator=self.TEXT_CARD_RESIDENT_TATARSTAN) == Notice.TEXT_CARD_RESIDENT_TATARSTAN
