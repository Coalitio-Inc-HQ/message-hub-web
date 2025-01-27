from fastapi_app.app import app
from core import logger
from fastapi_app.admin.admin import install_admin
from core.config_reader import config

if __name__ == "__main__":
    import uvicorn

    install_admin(app)
    
    try:
        uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)
    except KeyboardInterrupt:
        logger.debug("Приложение успешно остановлено")
    