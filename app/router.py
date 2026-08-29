from fastapi import APIRouter, HTTPException

from app.schemas.order_schema import CreateOrder, OrderEvent
from app.producer.order_producer import send_order
from logging import getLogger


logger = getLogger(__name__)
router = APIRouter()


@router.post('/order')
async def create_order(order: CreateOrder):
    order_event = OrderEvent(
        item_id=order.item_id,
        quantity=order.quantity,
        price=order.price
    )
    try:
        logger.info("Sending order event")
        await send_order(order_event)
    except Exception as ex:
        logger.error(f"POST request error: {ex}")
        raise HTTPException(status_code=503, detail="Service unavailable")
