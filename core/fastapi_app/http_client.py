import logging

from httpx import AsyncClient

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Пока что не используется. Изучаю, как правильно интегрировать
    """
    def __init__(self, base_url):
        self.HTTP_CLIENT = AsyncClient(base_url=base_url)

    async def close_connection(self):
        await self.HTTP_CLIENT.aclose()
        logger.info("Http соединение закрыто")
