from fastapi import APIRouter
from httpx import AsyncClient

from core import app_config, ChatDTO

router = APIRouter(prefix=f"{app_config.ROUTER_PREFIX}")


async def get_waiting_chats(count: int = 50) -> list[ChatDTO]:
    async with AsyncClient(base_url=app_config.BASE_DOMAIN) as client:
        try:
            response = await client.post("/get_list_of_waiting_chats",
                                         json={"count": count})
            response.raise_for_status()
            print(response)
            return response
        except Exception as e:
            print(f"Error: {e}")
