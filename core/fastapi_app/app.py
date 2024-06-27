from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.fastapi_app.main_client import internal_router
from core import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(internal_router)
    logger.info("Приложение успешно запущено")
    yield
    logger.info("Приложение успешно остановлено")


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run('app:app', host="localhost", port=8000, reload=True)
