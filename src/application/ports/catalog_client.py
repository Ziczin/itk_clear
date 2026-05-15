from abc import ABC, abstractmethod
from typing import Any


class CatalogServiceError(Exception):
    """Ошибка при возврате ответа от сервиса каталога"""


class ItemNotFoundInCatalogError(CatalogServiceError):
    """Ошибка при получении кода 404 от сервиса каталога"""


class InsufficientStockError(CatalogServiceError):
    """Ошибка при недостаточном количестве товара на складе"""


class ICatalogClient(ABC):
    """Абстрактный порт для взаимодействия с внешним каталогом"""

    @abstractmethod
    async def check_stock(self, item_id: str, quantity: int) -> dict[str, Any]:
        """
        Проверка доступности товара во внешнем инвентаре

        Аргументы:
            item_id: Уникальный идентификатор товара
            quantity: Запрашиваемое количество

        Возвращает:
            dict: Данные товара из каталога с информацией о наличии

        Исключения:
            ItemNotFoundInCatalogError: Если товар не найден в каталоге
            InsufficientStockError: Если доступное количество меньше запрошенного
            CatalogServiceError: При других ошибках уровня сервиса
        """
