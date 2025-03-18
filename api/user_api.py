import logging
import random
from typing import Dict
from requests import Response, request

logger = logging.getLogger("API")


class UserAPI:
    """
    Класс для управления созданием тестового пользователя через API.
    """
    CRM_URL = "***"
    WAY4_URL = "***"
    CRM_ADAPTER_URL = "***"
    BIZTALK_ID_URL = "***"
    SAVE_BIZTALK_ID_WAY4_URL = "***"
    SAVE_BIZTALK_ID_CRM_URL = "***"
    DIGITAL_CARD_URL = "***"
    CARD_INFO_URL = "***"
    PLASTIC_CARD_URL = "***"

    USERNAME = "your_username"
    PASSWORD = "your_password"

    @staticmethod
    def data_for_create_way4_user(user_crm=None):
        """
        Тело запроса для создания клиента в CRM.
        :param user_crm: Данные созданного клиента в CRM
        """
        data = {
                "clientInfo": {
                    "isResident": True,
                    "orderDprt": "0000",
                    "shortName": f"{user_crm['last_name']} {user_crm['first_name'][0]}. {user_crm['middle_name'][0]}.",
                    "firstName": user_crm["first_name"],
                    "lastName": user_crm["last_name"],
                    "middleName": user_crm["middle_name"],
                    "embossingFirstName": "NAME",
                    "embossingLastName": "CARDHOLDER",
                    "country": "RUS",
                    "language": "R",
                    "birthDate": "1994-09-09",
                    "birthPlace": "Казань",
                    "gender": "Male" if user_crm["sex"] == "Мужской" else "Female",
                    "maritalStatus": "Single",
                    "inn": None,
                    "email": user_crm["email"],
                    "tabelNumber": user_crm["crm_id"],
                    "companyCode": None,
                    "riskLevel": "R1",
                    "pdl": "NotApplicable",
                    "uek": None,
                    "comment": None,
                    "codeWord": None
                },
                "clientDocument": {
                    "regNumberType": "Passport",
                    "regSeries": user_crm["passport_series"].replace(" ", ""),
                    "regNumber": user_crm["passport_number"],
                    "regNumberDetails": user_crm["passport_issue_place"],
                    "regDate": "2014-10-10",
                    "departmentCode": user_crm["passport_division_code"]
                },
                "phoneList": {
                    "phoneMobile": user_crm["phone"],
                    "phoneHome": user_crm["phone"],
                    "phoneWork": user_crm["phone"]
                },
                "clientAddress": [
                    {
                        "addressType": "Registration",
                        "postalCode": "420021",
                        "country": "RUS",
                        "district": None,
                        "city": "Казань",
                        "street": "Татарстан",
                        "house": "20",
                        "flatNumber": "220",
                        "fullAddress": "Россия, 420021, д 20, кв 220"
                    }
                ]
            }
        return data

    @staticmethod
    def data_for_setting_way4_id_in_crm(crm_id=None, way4_id=None):
        """
        Тело запроса для проставления Way4Id в CRM
        :param crm_id: ID клиента в CRM
        :param way4_id: ID клиента в WAY4
        """
        data = {
                "clientType": "Individual",
                "crmId": crm_id,
                "clientAbsType": "WAY4",
                "clientAbsId": way4_id
            }
        return data

    @staticmethod
    def data_for_generate_biztalk_id(login=None):
        """
        Тело запроса для генерации biztalkId
        :param login: Логин тестового пользователя
        """
        data = {
                "login": login,
                "password": "***"
            }
        return data

    @staticmethod
    def data_for_save_biztalk_id_in_way4(way4_id=None, biztalk_id=None):
        """
        Тело запроса для генерации biztalkId
        :param way4_id: ID клиента в WAY4
        :param biztalk_id: ID после генерации biztalk
        """
        data = {
                "Way4Id": way4_id,
                "BankokId": biztalk_id
            }
        return data

    @staticmethod
    def data_for_save_biztalk_id_in_crm(crm_id=None, biztalk_id=None):
        """
        Тело запроса для генерации biztalkId
        :param crm_id: ID клиента в CRM
        :param biztalk_id: ID после генерации biztalk
        """
        data = {
                "searchSystem": {
                    "name": "CRM",
                    "clientID": crm_id
                },
                "insertSystem": {
                    "name": "BANKOK",
                    "clientID": biztalk_id
                }
            }
        return data

    @staticmethod
    def data_for_issue_digital_card(way4_id=None, first_name=None, last_name=None, middle_name=None):
        """
        Тело запроса для выпуска цифровой Карты Жителя
        :param way4_id: ID клиента в WAY4
        :param first_name: Имя клиента
        :param last_name: Фамилия клиента
        :param middle_name: Отчество клиента
        """
        data = {
                "client": {
                    "way4Id": way4_id,
                    "firstName": first_name,
                    "lastName": last_name,
                    "middleName": middle_name,
                    "embFirstName": "NAME",
                    "embLastName": "CARDHOLDER",
                    "department": "0000"
                },
                "contract": {
                    "card": {
                        "expProd": False,
                        "productCode": "***",
                        "department": "0000"
                    },
                    "productCode": "***",
                    "department": "0000"
                }
            }
        return data

    @staticmethod
    def data_for_get_info_by_card(card_id=None):
        """
        Тело запроса для получения информации о карте
        :param card_id: ID выпущенной карты в Bankok
        """
        data = {
                "CardId": card_id
            }
        return data

    @classmethod
    def create_crm_user(cls, url_api=CRM_URL, header=None, data=None, status_code=200) -> Dict:
        """
        Создание клиента в CRM.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Создание клиента в CRM. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()[0]}")
        assert res.status_code == status_code
        return res.json()[0]

    @classmethod
    def create_way4_user(cls, url_api=WAY4_URL, header=None, data=None, status_code=200) -> Response:
        """
        Создание клиента в WAY4.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Создание клиента в WAY4. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()}")
        assert res.status_code == status_code
        return res.json()

    @classmethod
    def setting_way4_id_in_crm(cls, url_api=CRM_ADAPTER_URL, header=None, data=None, status_code=200) -> Response:
        """
        Проставление Way4Id в CRM.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Проставление Way4Id в CRM. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()}")
        assert res.status_code == status_code
        return res.json()

    @classmethod
    def generate_biztalk_id(cls, url_api=BIZTALK_ID_URL, header=None, data=None, status_code=200) -> Response:
        """
        Генерация biztalkId.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Генерация biztalkId. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()}")
        assert res.status_code == status_code
        return res.json()

    @classmethod
    def save_biztalk_id_way4(cls, url_api=SAVE_BIZTALK_ID_WAY4_URL, header=None, data=None,
                             status_code=200) -> Response:
        """
        Сохранение biztalkId в Way4.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Сохранение biztalkId в Way4. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()}")
        assert res.status_code == status_code
        return res.json()

    @classmethod
    def save_biztalk_id_crm(cls, url_api=SAVE_BIZTALK_ID_CRM_URL, header=None, data=None, status_code=200) -> Response:
        """
        Сохранение biztalkId в CRM.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Сохранение biztalkId в CRM. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()}")
        assert res.status_code == status_code
        return res.json()

    @classmethod
    def issue_digital_card(cls, url_api=DIGITAL_CARD_URL, header=None, data=None, status_code=200) -> Dict:
        """
        Выпуск цифровой Карты Жителя.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Выпуск цифровой КЖ. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()}")
        assert res.status_code == status_code
        return res.json()

    @classmethod
    def get_info_by_card(cls, url_api=CARD_INFO_URL, header=None, data=None, status_code=200) -> Response:
        """
        Получение информации о карте.
        :param url_api: URL версии API;
        :param header: Токен авторизации;
        :param data: Тело запроса;
        :param status_code: Ожидаемый ответ сервера;
        """
        res = request(
            method="POST",
            url=url_api,
            headers=header,
            json=data
        )
        logger.info(f"POST: Инфо о карте. Ответ: {res.status_code}")
        logger.info(f"JSON ответа: {res.json()}")
        assert res.status_code == status_code
        return res.json()

    @classmethod
    def create_test_user(cls) -> Dict:
        """Последовательное выполнение всех API-запросов для создания пользователя."""
        user_crm = cls.create_crm_user()
        user_way4 = cls.create_way4_user(data=cls.data_for_create_way4_user(user_crm=user_crm))
        cls.setting_way4_id_in_crm(data=cls.data_for_setting_way4_id_in_crm(
            crm_id=str(user_crm["crm_id"]), way4_id=str(user_way4["result"]["client"]["way4Id"])))
        test_user_login = f"user{random.randint(1, 100000000000)}"
        biztalk_id = cls.generate_biztalk_id(data=cls.data_for_generate_biztalk_id(login=test_user_login))
        cls.save_biztalk_id_way4(data=cls.data_for_save_biztalk_id_in_way4(
            way4_id=str(user_way4["result"]["client"]["way4Id"]), biztalk_id=biztalk_id["result"]))
        cls.save_biztalk_id_crm(data=cls.data_for_save_biztalk_id_in_crm(
            crm_id=str(user_crm["crm_id"]), biztalk_id=biztalk_id["result"]))
        card_id = cls.issue_digital_card(data=cls.data_for_issue_digital_card(
            way4_id=str(user_way4["result"]["client"]["way4Id"]), first_name=user_crm["first_name"],
            last_name=user_crm["last_name"], middle_name=user_crm["middle_name"]))
        card_info = cls.get_info_by_card(data=cls.data_for_get_info_by_card(
            card_id=card_id["result"]["contract"]["card"]["id"]))
        user_crm.update(card_info)
        return user_crm
