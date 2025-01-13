from fastapi_app.app import app
from core import logger
from fastapi_app.admin.admin import install_admin

if __name__ == "__main__":
    import uvicorn

    install_admin(app)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        logger.debug("Приложение успешно остановлено")
    