import asyncio
from typing import Any

import aiohttp
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import settings
from src.utils.logger import logger


class PaymentServiceError(Exception):
    """Raised when payment service returns an error."""

    ...


def setup_retry_decorator(order_id: str):
    """Создаёт декоратор retry с логированием попыток."""
    logger.info(
        "PAYMENT CLIENT | Settings of retry config attempts",
        attempts=settings.PAYMENTS_RETRY_LIMIT,
        start_timeout=settings.PAYMENTS_START_TIMEOUT,
        max_timeout=settings.PAYMENTS_MAX_TIMEOUT,
    )

    def before_sleep(retry_state):
        attempt = retry_state.attempt_number
        exception = retry_state.outcome.exception()
        logger.warning(
            "PAYMENT CLIENT | Payment attempt failed, retrying",
            attempt=attempt,
            error=str(exception),
            order_id=order_id,
        )

    return retry(
        stop=stop_after_attempt(settings.PAYMENTS_RETRY_LIMIT),
        wait=wait_exponential(
            multiplier=settings.PAYMENTS_START_TIMEOUT,
            max=settings.PAYMENTS_MAX_TIMEOUT,
        ),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        after=after_log(logger, "WARNING"),
        before_sleep=before_sleep,
        retry_error_callback=lambda state: state.outcome.result(),
    )


class PaymentClient:
    """HTTP client for payment gateway communication."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize client with aiohttp session."""
        self.session = session

    async def _do_create_payment(
        self, url: str, payload: dict[str, Any], headers: dict[str, str], order_id: str
    ) -> dict[str, Any]:
        """Выполняет POST-запрос к платежному сервису."""
        async with self.session.post(url, json=payload, headers=headers) as response:
            response_text = await response.text()

            if response.status not in (200, 201):
                logger.error(
                    "PAYMENT CLIENT | Payment request failed",
                    status=response.status,
                    error=response_text,
                    order_id=order_id,
                )
                raise PaymentServiceError(
                    f"PAYMENT CLIENT | Payment API error: {response.status} - {response_text}"
                )

            result: dict[str, Any] = await response.json()
            logger.info(
                "PAYMENT CLIENT | Payment created",
                payment_id=result.get("id"),
                order_id=order_id,
            )
            return result

    async def create(
        self, order_id: str, amount: str, idempotency_key: str
    ) -> dict[str, Any]:
        """Initialize a payment session with the external provider."""
        callback_url = settings.PAYMENTS_CALLBACK_URL
        url = f"{settings.PAYMENTS_URL}/api/payments"

        payload: dict[str, Any] = {
            "order_id": order_id,
            "amount": amount,
            "callback_url": str(callback_url),
            "idempotency_key": idempotency_key,
        }

        headers: dict[str, str] = {
            "X-API-Key": settings.CAPASHINO_API_KEY,
            "Content-Type": "application/json",
        }

        logger.info(
            "PAYMENT CLIENT | Requesting payment creation",
            order_id=order_id,
            payload=payload,
            callback_url=callback_url,
        )

        retry_decorator = setup_retry_decorator(order_id)
        return await retry_decorator(self._do_create_payment)(
            url=url, payload=payload, headers=headers, order_id=order_id
        )
