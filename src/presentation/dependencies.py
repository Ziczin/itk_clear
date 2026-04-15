import aiohttp
from fastapi import Depends
from src.infrastructure.uow import UoW
from src.infrastructure.clients.catalog import CatalogClient
from src.infrastructure.clients.payment import PaymentClient
from src.infrastructure.clients.notify import NotifyClient
from src.application.usecases.create_order import CreateOrderUseCase
from src.application.usecases.get_order import GetOrderUseCase
from src.application.usecases.payment_callback import PaymentCallbackUseCase
from src.utils.logger import logger


def provide_unit_of_work():
    """Instantiate and return a new transactional unit of work."""
    return UoW()


def provide_http_session():
    """Retrieve shared aiohttp client session from application state."""
    logger.info("Try to retrieve HTTP session")
    return aiohttp.ClientSession()


def provide_catalog_client(session=Depends(provide_http_session)):
    """Construct catalog HTTP client with injected session."""
    return CatalogClient(session=session)


def provide_payment_client(session=Depends(provide_http_session)):
    """Construct payment HTTP client with injected session."""
    return PaymentClient(session=session)


def provide_notification_client(session=Depends(provide_http_session)):
    """Construct notification HTTP client with injected session."""
    return NotifyClient(session=session)


def provide_create_order_use_case(
    uow=Depends(provide_unit_of_work),
    catalog=Depends(provide_catalog_client),
    payment=Depends(provide_payment_client),
    notify=Depends(provide_notification_client),
):
    """Assemble order creation use case with all required dependencies."""
    return CreateOrderUseCase(
        uow=uow,
        catalog_client=catalog,
        payment_client=payment,
        notification_client=notify,
    )


def provide_get_order_use_case(uow=Depends(provide_unit_of_work)):
    """Assemble order retrieval use case with required dependencies."""
    return GetOrderUseCase(uow=uow)


def provide_payment_callback_use_case(
    uow=Depends(provide_unit_of_work), notify=Depends(provide_notification_client)
):
    """Assemble payment callback processing use case with dependencies."""
    return PaymentCallbackUseCase(uow=uow, notification_client=notify)
