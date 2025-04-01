from fastapi_app.app import app
from core import logger
from core.config_reader import config

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT, forwarded_allow_ips="*", proxy_headers=True)
    except KeyboardInterrupt:
        logger.debug("Приложение успешно остановлено")
    