class OrderError(Exception):
    pass


class OrderNotFoundError(OrderError):
    pass


class InsufficientStockError(OrderError):
    pass


class CatalogServiceError(OrderError):
    pass


class PaymentServiceError(OrderError):
    pass


class NotificationServiceError(OrderError):
    pass
