from fastapi_app.app import app
from core import logger

if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.debug("Приложение успешно остановлено")
