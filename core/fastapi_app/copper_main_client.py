import httpx
from core.config_reader import config

class CopperMainClient:
    def __init__(self):
        self.base_url = config.COPPER_MAIN_URL

    async def register_platform(self, url: str, platform_name: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/register_platform", 
                json={"url": url, "platform_name": platform_name}
            )
            response.raise_for_status()
            return response.json()

    async def register_user(self, platform_name: str, user_firstname: str) -> int:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/register_user", 
                json={"platform_name": platform_name, "user_firstname": user_firstname}
            )
            response.raise_for_status()
            return response.json()["user_id"]

    async def get_waiting_chats(self, user_id: int) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/waiting_chats/{user_id}")
            response.raise_for_status()
            return response.json()

    async def read_chat_by_user(self, user_id: int, chat_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/read_chat/{user_id}/{chat_id}")
            response.raise_for_status()
            return response.json()

    async def add_user_to_chat(self, user_id: int, chat_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/add_user_to_chat", 
                json={"user_id": user_id, "chat_id": chat_id}
            )
            response.raise_for_status()
            return response.json()

    async def get_chats_by_user(self, user_id: int) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/user_chats/{user_id}")
            response.raise_for_status()
            return response.json()

    async def get_messages_from_chat(self, chat_id: int, count: int) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/messages/{chat_id}?count={count}")
            response.raise_for_status()
            return response.json()

    async def send_message_to_chat(self, message: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/send_message", 
                json=message
            )
            response.raise_for_status()
            return response.json()
