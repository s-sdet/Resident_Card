import pytest
from pytest_testrail.plugin import pytestrail


class TestIssuingPlasticCard:
    """Тесты для выпуска пластиковой карты жителя с главного экрана приложения."""

    @pytest.mark.core
    @pytest.mark.limited
    @pytestrail.case("C15798752")
    def test_issuing_resident_plastic_card_from_main_screen(self, app, issue_plastic_card):
        """Тест выпуска пластиковой карты жителя с главного экрана приложения."""
        pass  # Вся логика теста в фикстуре issue_plastic_card

    @pytest.mark.core
    @pytestrail.case("C15798875")
    def test_assert_city_can_get_card(self, app, issue_plastic_card):
        """Тест выдачи карты - ввод города, в котором возможно получить карту."""
        app.main.input_delivery_city()
        app.main.select_delivery_option()

    @pytest.mark.core
    @pytestrail.case("C15798876", "C15798877")
    @pytest.mark.parametrize("city", ["Нальчик", "Казанфр"])
    def test_assert_city_cant_get_card(self, app, issue_plastic_card, city):
        """Тест выдачи карты в городе, в котором невозможно получить карту."""
        app.main.input_delivery_invalid_city(city=city)

    @pytest.mark.core
    @pytestrail.case("C15798903", "C15798899")
    @pytest.mark.parametrize("delivery_method", ["bank", "courier"])
    def test_how_to_get_card(self, app, issue_plastic_card, delivery_method):
        """Тест выбора способа получения карты: курьером или в отделении банка."""
        app.main.input_delivery_city()
        app.main.how_to_get_card(delivery_method)

    @pytest.mark.limited
    @pytestrail.case("C15798904")
    def test_select_branch_to_receive_card(self, app, issue_plastic_card):
        """Позитивный тест выбора отделения банка для получения выпущенной пластиковой карты."""
        app.main.input_delivery_city()
        app.main.receive_card_from_bank()
        app.main.select_branch_to_receive_card()

    @pytest.mark.core
    @pytestrail.case("C24016538")
    def test_go_to_page_to_enter_address(self, app, issue_plastic_card):
        """Тест переход на страницу ввода адреса курьерской доставки."""
        app.main.input_delivery_city()
        app.main.receive_card_by_courier()
        app.main.open_page_to_input_address()

    @pytest.mark.core
    @pytestrail.case("C15798900")
    def test_courier_delivery_change_city(self, app, issue_plastic_card):
        """Тест смена города курьерской доставки."""
        app.main.input_delivery_city()
        app.main.receive_card_by_courier()
        app.main.courier_delivery_change_city()

    @pytest.mark.core
    @pytestrail.case("C15798901", "C15798902")
    @pytest.mark.parametrize("delivery_method", ["valid", "invalid"])
    def test_assert_delivery_address(self, app, issue_plastic_card, delivery_method):
        """Тест проверки валидного и невалидного адреса доставки пластиковой карты."""
        app.main.input_delivery_city(city="Казань")
        app.main.receive_card_by_courier()
        app.main.open_page_to_input_address()
        app.main.validate_input_delivery_address(method=delivery_method)

    @pytest.mark.limited
    @pytestrail.case("C15810130")
    @pytest.mark.parametrize("issue_plastic_card", [True], indirect=True)
    def test_delivery_card_to_bank_branch(self, app, issue_plastic_card):
        """
        Тест оформления доставки карты в отделение банка.
        Передаем indirect=True для удаления пользователя в data/users/users_list.txt после успешного выполнения теста.
        """
        app.main.input_delivery_city()
        app.main.receive_card_from_bank()
        app.main.select_branch_to_receive_card()
        app.main.order_card()

    @pytest.mark.core
    @pytestrail.case("C15811662")
    @pytest.mark.parametrize("issue_plastic_card", [True], indirect=True)
    def test_return_to_main_screen_after_ordering_card(self, app, issue_plastic_card):
        """
        Тест возврата на главный экран после успешного оформления карты.
        Передаем indirect=True для удаления пользователя в data/users/users_list.txt после успешного выполнения теста.
        """
        app.main.input_delivery_city()
        app.main.receive_card_from_bank()
        app.main.select_branch_to_receive_card()
        app.main.order_card()
        app.main.return_to_home_screen()

    @pytest.mark.limited
    @pytestrail.case("C15810129")
    @pytest.mark.parametrize("issue_plastic_card", [True], indirect=True)
    def test_card_delivery_by_courier(self, app, issue_plastic_card, city: str = "Казань"):
        """
        Тест оформления доставки карты курьером.
        Передаем indirect=True для удаления пользователя в data/users/users_list.txt после успешного выполнения теста.
        """
        app.main.input_delivery_city(city=city)
        app.main.receive_card_by_courier()
        app.main.open_page_to_input_address()
        app.main.input_delivery_address()
        app.main.confirm_delivery_address()
        app.main.order_card()
