import asyncio

from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError

from app.config import settings
import logging

from app.schemas.order_schema import OrderEvent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def start_consumer():
    consumer = AIOKafkaConsumer(
        settings.TOPIC_NAME,
        bootstrap_servers=settings.KAFKA_SERVER,
        group_id=settings.CONSUMER_GROUP
    )
    await consumer.start()
    logger.info(f"Consumer started successfully. Connected to group '{settings.CONSUMER_GROUP}'")

    try:
        async for message in consumer:
            try:
                order_event = OrderEvent.model_validate_json(message.value)
                logger.info(f"Consumer event loaded: {order_event}")
                await asyncio.sleep(0.5)
            except ValidationError as ex:
                logger.error(f"Validation error during message conversion: {ex}")
    finally:
        logger.info("Shutting down consumer...")
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(start_consumer())
