from pydantic_settings import BaseSettings


class OrderSettings(BaseSettings):
    KAFKA_SERVER: str = "localhost:9092"
    TOPIC_NAME: str = "order-events"
    CONSUMER_GROUP: str = "order-processor-group"

settings = OrderSettings()
