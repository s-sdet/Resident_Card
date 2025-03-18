from __future__ import annotations
import re
from typing import Optional
import time
import requests


class OTPUrls:
    NOTIFICATIONS = '***'
    CONFIRMATION = '***'


class OTPRequestHelper:

    def __init__(self,
                 biztalk_id: Optional[str] = None,
                 phone: Optional[str] = None):
        self.biztalk_id = biztalk_id if biztalk_id is not None else ''
        self.phone = phone if phone is not None else ''

    def get_notifications(self) -> OTPResponseParser:
        """
            Выполнить запрос получения списка сообщений с кодами,
            используя бизталк ид и (или) телефонный номер
        """
        time.sleep(4)  # - позволяет дождаться необходимого ОТП кода на беке
        service_response = requests.post(
            url=OTPUrls.NOTIFICATIONS,
            json={
                'phone': self.phone,
                'biztalkId': self.biztalk_id
            },
            verify=False
        )
        return OTPResponseParser(service_response.json())


class OTPResponseParser:

    def __init__(self, json: dict):
        self._json = json
        self._search_patterns = {
            'LOGIN': re.compile(r'AKBARS Для входа введите код. Не сообщайте его никому: (?P<sms_code>\d{5})'),
            'SIGN_DOCUMENTS': re.compile(
                r'(?P<sms_code>\d{5}) - ваш код для подтверждения подписания документов. Не сообщайте его никому.'
            ),
            'CLOSE_DEPOSIT': re.compile(
                r'Для закрытия вклада введите код: (?P<sms_code>\d{5}). Не сообщайте его никому'
            ),
            'PAYMENT': 'ваш код для подтверждения платежа',
            'CHANGE_CARD_PIN_CODE': re.compile(
                r'Для подтверждения смены пинкода введите код (?P<sms_code>\d{5})'),
            'CHANGE_SMS_TARIFF': re.compile(
                r'Для подключения пакета .+ введите код. Не сообщайте его никому: (?P<sms_code>\d{5})'),
        }

    def _parse_by_pattern(self, pattern_key: str):
        """Поиск паттерна сообщения в json и возврат СМС кода"""
        for operation in self._json:
            match = re.fullmatch(pattern=self._search_patterns[pattern_key],
                                 string=operation['message'])
            if match:
                return match.group('sms_code')

        raise ValueError(
            f'Не удалось найти сообщения, удовлетворяющие шаблону: {self._search_patterns[pattern_key]}'
        )

    def get_login_code(self) -> str:
        """Получить ОТП код для логина"""
        return self._parse_by_pattern('LOGIN')

    def get_sign_documents_code(self) -> str:
        """Получить ОТП код для подписи документа"""
        return self._parse_by_pattern('SIGN_DOCUMENTS')

    def get_confirm_close_deposit_code(self) -> str:
        """Получить ОТП код при закрытии депозита"""
        return self._parse_by_pattern('CLOSE_DEPOSIT')

    def get_change_pin_code(self) -> str:
        """Получить ОТП код для смены пин-кода карты"""
        return self._parse_by_pattern('CHANGE_CARD_PIN_CODE')

    def get_change_sms_tariff(self) -> str:
        """Получить ОТП код для смены тарифа смс уведомлений"""
        return self._parse_by_pattern('CHANGE_SMS_TARIFF')
