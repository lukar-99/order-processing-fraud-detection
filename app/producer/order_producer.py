from logging import getLogger
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential

from app.config import settings
from app.schemas.order_schema import OrderEvent

logger = getLogger(__name__)
producer: AIOKafkaProducer | None = None


@retry(
    retry=retry_if_exception_type((KafkaConnectionError, ConnectionRefusedError, OSError, KafkaError)),
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
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
