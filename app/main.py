from logging import getLogger
from app.producer.order_producer import start_kafka, stop_kafka
from app.router import router
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_kafka()
    yield

    await stop_kafka()

app = FastAPI(lifespan=lifespan)
app.include_router(router)

