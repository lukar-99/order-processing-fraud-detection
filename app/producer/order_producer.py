from logging import getLogger
from aiokafka import AIOKafkaProducer
from app.config import settings
from app.schemas.order_schema import OrderEvent

logger = getLogger(__name__)
producer: AIOKafkaProducer | None = None


async def start_kafka():
    logger.info("Starting Kafka server")

    global producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_SERVER)

    await producer.start()

async def stop_kafka():
    if producer:
        await producer.stop()
    else:
        logger.info("Kafka server not running")

async def send_order(event: OrderEvent):
    if producer is None:
        raise RuntimeError("Kafka producer is not initialized")

    kafka_event = event.model_dump_json()
    logger.info(f"Json order event: {kafka_event}")

    kafka_event = kafka_event.encode("utf-8")
    logger.info("Sending byte event to kafka")

    await producer.send_and_wait(settings.TOPIC_NAME, kafka_event)
