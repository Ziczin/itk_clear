from abc import ABC, abstractmethod


class NotifyServiceError(Exception):
    """Ошибка при возврате ответа от сервиса уведомлений"""


class INotifyClient(ABC):
    """Абстрактный порт для отправки уведомлений пользователям"""

    @abstractmethod
    async def send(
        self,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ) -> bool:
        """
        Отправка уведомления с гарантированной идемпотентностью

        Аргументы:
            message: Текст уведомления
            reference_id: Уникальный идентификатор для отслеживания
            idempotency_key: Ключ для предотвращения дублирования отправки

        Возвращает:
            bool: True если уведомление успешно отправлено, False иначе

        Исключения:
            NotifyServiceError: При ошибке возврата от сервиса уведомлений
        """
