from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from core.database.schemas import UserCreate
from .copper_main_client import CopperMainClient

copper_client = CopperMainClient()

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_waiting_chats(user_id: int):
    return await copper_client.get_waiting_chats(user_id)

async def read_chat_by_user(user_id: int, chat_id: int):
    return await copper_client.read_chat_by_user(user_id, chat_id)

async def add_user_to_chat(user_id: int, chat_id: int):
    await copper_client.add_user_to_chat(user_id, chat_id)

async def get_chats_by_user(user_id: int):
    return await copper_client.get_chats_by_user(user_id)

async def get_messages_from_chat(chat_id: int, count: int):
    return await copper_client.get_messages_from_chat(chat_id, count)

async def send_message_to_chat(message):
    await copper_client.send_message_to_chat(message.dict())
