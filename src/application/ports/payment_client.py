from abc import ABC, abstractmethod
from typing import Any


class PaymentServiceError(Exception):
    """Ошибка при возврате ответа от платежного сервиса"""


class IPaymentClient(ABC):
    """Абстрактный порт для создания платежей через внешнего провайдера"""

    @abstractmethod
    async def create(
        self,
        order_id: str,
        amount: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """
        Инициализация платежной сессии у внешнего провайдера

        Аргументы:
            order_id: Идентификатор заказа в системе
            amount: Сумма платежа в виде строки для точности
            idempotency_key: Ключ идемпотентности для безопасных повторных запросов

        Возвращает:
            dict: Ответ платежного шлюза с данными платежа

        Исключения:
            PaymentServiceError: При ошибке возврата от платежного сервиса
        """
