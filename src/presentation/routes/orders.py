from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from src.presentation.schemas.order import CreateOrderRequest, OrderResponse
from src.application.usecases.create_order import CreateOrderUseCase
from src.application.usecases.get_order import GetOrderUseCase
from src.application.ports.order_repo import OrderNotFoundError, OrderDuplicateError
from src.infrastructure.clients.catalog import (
    CatalogServiceError,
    ItemNotFoundInCatalogError,
)
from src.infrastructure.clients.payment import PaymentServiceError
from src.utils.logger import logger
from src.presentation.dependencies import (
    provide_create_order_use_case,
    provide_get_order_use_case,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(provide_create_order_use_case),
):
    """Handle order creation requests."""
    logger.debug("Route /api/orders")
    logger.info(
        "Handling CreateOrder request",
        user_id=request.user_id,
        item_id=str(request.item_id),
    )

    try:
        logger.debug("Try to process usecase")

        order = await use_case.execute(
            user_id=request.user_id,
            item_id=request.item_id,
            quantity=request.quantity,
            idempotency_key=request.idempotency_key,
        )

        logger.info("Order creation successful", order_id=str(order.id))
        logger.debug("Route /api/orders returns 200")

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat(),
            payment_id=order.payment_id,
        )

    except OrderDuplicateError:
        logger.warning(
            "Duplicate order request", idempotency_key=str(request.idempotency_key)
        )

        existing = await use_case.uow.orders.get_by_idempotency_key(
            request.idempotency_key
        )

        if existing:
            logger.debug("Route /api/orders returns 200, existing order")
            return OrderResponse(
                id=existing.id,
                user_id=existing.user_id,
                item_id=existing.item_id,
                quantity=existing.quantity,
                status=existing.status,
                created_at=existing.created_at.isoformat(),
                updated_at=existing.updated_at.isoformat(),
            )

        logger.debug("Route /api/orders returns 409")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key already used",
        )

    except (CatalogServiceError, PaymentServiceError) as e:
        logger.error("External service error", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except ItemNotFoundInCatalogError as e:
        logger.error("Item ", error=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except OrderNotFoundError as e:
        logger.error(f"Order with id: {request.item_id} not found", error=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.exception("Order creation failed unexpectedly", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            error=str(e),
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID, use_case: GetOrderUseCase = Depends(provide_get_order_use_case)
):
    """Retrieve order details by unique identifier."""
    logger.debug(r"Route /api/orders/{order_id}")
    logger.info("Fetching order details", order_id=str(order_id))

    try:
        order = await use_case.execute(order_id=order_id)

        logger.info("Order retrieved successfully", status=order.status)
        logger.debug(r"Route /api/orders/{order_id} returns 200")

        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status.value,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat(),
        )

    except OrderNotFoundError:
        logger.warning("Order not found", order_id=str(order_id))
        logger.debug(r"Route /api/orders/{order_id} returns 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    except Exception as e:
        logger.exception("Order retrieval failed", error=str(e))
        logger.debug(r"Route /api/orders/{order_id} returns 500")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
