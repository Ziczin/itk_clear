from fastapi import Request, Depends
from src.infrastructure.uow import UoW
from src.infrastructure.clients.catalog import CatalogClient
from src.infrastructure.clients.payment import PaymentClient
from src.infrastructure.clients.notify import NotifyClient
from src.application.usecases.create_order import CreateOrderUC
from src.application.usecases.get_order import GetOrderUC
from src.application.usecases.payment_callback import PaymentCallbackUC


def get_uow():
    """Provide transactional unit per HTTP request."""
    return UoW()


def get_http_session(request: Request):
    """Inject shared aiohttp session from app state."""
    return request.app.state.http_session


def get_catalog(session=Depends(get_http_session)):
    """Initialize catalog client dependency."""
    return CatalogClient(session)


def get_payment(session=Depends(get_http_session)):
    """Initialize payment client dependency."""
    return PaymentClient(session)


def get_notify(session=Depends(get_http_session)):
    """Initialize notification client dependency."""
    return NotifyClient(session)


def get_create_uc(
    uow=Depends(get_uow),
    cat=Depends(get_catalog),
    pay=Depends(get_payment),
    notify=Depends(get_notify),
):
    """Assemble create order use case with all dependencies."""
    return CreateOrderUC(uow, cat, pay, notify)


def get_get_order_uc(uow=Depends(get_uow)):
    """Assemble get order use case with dependencies."""
    return GetOrderUC(uow)


def get_callback_uc(uow=Depends(get_uow), notify=Depends(get_notify)):
    """Assemble payment callback use case with dependencies."""
    return PaymentCallbackUC(uow, notify)
