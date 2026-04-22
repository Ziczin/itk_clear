from aiohttp import ClientSession
from fastapi import Depends, Request

from src.application.usecases.create_order import CreateOrderUseCase
from src.application.usecases.get_order import GetOrderUseCase
from src.application.usecases.payment_callback import PaymentCallbackUseCase
from src.infrastructure.clients.catalog import CatalogClient
from src.infrastructure.clients.notify import NotifyClient
from src.infrastructure.clients.payment import PaymentClient
from src.infrastructure.uow import UoW
from src.utils.logger import logger


def provide_unit_of_work() -> UoW:
    """Instantiate and return a new transactional unit of work."""
    return UoW()


def provide_http_session(request: Request) -> ClientSession:
    """Retrieve shared aiohttp client session from application state."""
    logger.info("DEPENDENCY | Retrieving HTTP session from application state")
    return request.app.state.http_session  # type: ignore[no-any-return]


def provide_catalog_client(
    session: ClientSession = Depends(provide_http_session),
) -> CatalogClient:
    """Construct catalog HTTP client with injected session."""
    return CatalogClient(session=session)


def provide_payment_client(
    session: ClientSession = Depends(provide_http_session),
) -> PaymentClient:
    """Construct payment HTTP client with injected session."""
    return PaymentClient(session=session)


def provide_notification_client(
    session: ClientSession = Depends(provide_http_session),
) -> NotifyClient:
    """Construct notification HTTP client with injected session."""
    return NotifyClient(session=session)


def provide_create_order_use_case(
    uow: UoW = Depends(provide_unit_of_work),
    catalog: CatalogClient = Depends(provide_catalog_client),
    payment: PaymentClient = Depends(provide_payment_client),
    notify: NotifyClient = Depends(provide_notification_client),
) -> CreateOrderUseCase:
    """Assemble order creation use case with all required dependencies."""
    return CreateOrderUseCase(
        uow=uow,
        catalog_client=catalog,
        payment_client=payment,
        notification_client=notify,
    )


def provide_get_order_use_case(
    uow: UoW = Depends(provide_unit_of_work),
) -> GetOrderUseCase:
    """Assemble order retrieval use case with required dependencies."""
    return GetOrderUseCase(uow=uow)


def provide_payment_callback_use_case(
    uow: UoW = Depends(provide_unit_of_work),
    notify: NotifyClient = Depends(provide_notification_client),
) -> PaymentCallbackUseCase:
    """Assemble payment callback processing use case with dependencies."""
    return PaymentCallbackUseCase(uow=uow, notification_client=notify)
