import asyncio
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from src.config import settings
from src.utils.logger import logger
from aiohttp import TraceConfig
from contextlib import asynccontextmanager


class PaymentServiceError(Exception):
    """Raised when payment service returns an error."""

    pass


def setup_trace_config(order_id) -> TraceConfig:
    """Trace config для отслеживания попыток ретрая"""
    trace_config = TraceConfig()

    async def on_request_start(session, ctx, params):
        attempt = ctx.trace_request_ctx.get("current_attempt", 0) + 1
        logger.debug("Payment attempt", attempt=attempt, order_id=order_id)

    async def on_request_exception(session, ctx, params):
        attempt = ctx.trace_request_ctx.get("current_attempt", 0) + 1
        logger.warning(
            "Payment attempt failed",
            attempt=attempt,
            error=str(params.exception),
            order_id=order_id,
        )

    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_exception.append(on_request_exception)
    return trace_config


def setup_retry_options() -> ExponentialRetry:
    return ExponentialRetry(
        attempts=settings.PAYMENTS_RETRY_LIMIT,
        start_timeout=settings.PAYMENTS_START_TIMEOUT,
        max_timeout=settings.PAYMENTS_MAX_TIMEOUT,
        exceptions={aiohttp.ClientError, asyncio.TimeoutError},
        statuses={500, 502, 503, 504},
    )


@asynccontextmanager
async def post_to_payment_service(
    *, session, url, payload, headers, trace_config, retry_options
):
    async with RetryClient(
        client_session=session, trace_configs=[trace_config]
    ) as retry_client:
        async with retry_client.post(
            url,
            json=payload,
            headers=headers,
            retry_options=retry_options,
            trace_request_ctx={},
        ) as response:
            yield response


class PaymentClient:
    """HTTP client for payment gateway communication."""

    def __init__(self, session: aiohttp.ClientSession):
        """Initialize client with aiohttp session."""
        self.session = session

    async def create(self, order_id: str, amount: str, idempotency_key: str) -> dict:
        """Initialize a payment session with the external provider."""
        logger.info("Client.Payment.Create")
        callback_url = settings.PAYMENTS_CALLBACK_URL
        url = f"{settings.PAYMENTS_URL}/api/payments"

        payload = {
            "order_id": order_id,
            "amount": amount,
            "callback_url": str(callback_url),
            "idempotency_key": idempotency_key,
        }

        headers = {
            "X-API-Key": settings.CAPASHINO_API_KEY,
            "Content-Type": "application/json",
        }

        logger.info(
            "Requesting payment creation",
            order_id=order_id,
            callback_url=callback_url,
        )
        trace_config = setup_trace_config(order_id)
        retry_options = setup_retry_options()

        async with post_to_payment_service(
            sesion=self.session,
            order_id=order_id,
            url=url,
            payload=payload,
            headers=headers,
            trace_config=trace_config,
            retry_options=retry_options,
        ) as response:
            response_text = await response.text()

            if response.status not in (200, 201):
                logger.error(
                    "Payment request failed",
                    status=response.status,
                    error=response_text,
                    order_id=order_id,
                )
                raise PaymentServiceError(
                    f"Payment API error: {response.status} - {response_text}"
                )

            result = await response.json()
            logger.info(
                "Payment created", payment_id=result.get("id"), order_id=order_id
            )
            return result
