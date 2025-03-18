from fixtures.screens.base_screen import BaseScreen
from fixtures.screens.main_screen import MainScreen


class Application:
    """
    Класс-агрегатор для всех экранов приложения.
    Позволяет удобно обращаться к любому экрану через экземпляр `app`.
    """

    def __init__(self, driver):
        self.driver = driver
        self.base = BaseScreen(driver)
        self.main = MainScreen(driver)
