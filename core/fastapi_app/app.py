import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.database import async_session, create_db_and_tables
from ..database import crud
from core.database import schemas

app = FastAPI()

# @app.on_event("startup")
# async def startup():
#     await create_db_and_tables()

# async def get_db():
#     async with async_session() as session:
#         yield session

@app.post("/register_platform/")
async def register_platform(url: str, platform_name: str):
    await crud.copper_client.register_platform(url, platform_name)
    return {"message": "Platform registered successfully"}

@app.post("/register_user/", response_model=schemas.User)
async def register_user(platform_name: str, user_firstname: str, db: AsyncSession = Depends(get_db)):
    user_id = await crud.copper_client.register_user(platform_name, user_firstname)
    new_user = schemas.UserCreate(name=user_firstname)
    user = await crud.create_user(db, new_user)
    user.id = user_id  # Обновляем ID
    return user

@app.get("/waiting_chats/{user_id}", response_model=list[schemas.Chat])
async def get_waiting_chats(user_id: int):
    chats = await crud.get_waiting_chats(user_id)
    if not chats:
        raise HTTPException(status_code=404, detail="No waiting chats found")
    return chats

@app.post("/read_chat/", response_model=schemas.Chat)
async def read_chat_by_user(user_id: int, chat_id: int):
    chat = await crud.read_chat_by_user(user_id, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.post("/add_user_to_chat/")
async def add_user_to_chat(user_id: int, chat_id: int):
    await crud.add_user_to_chat(user_id, chat_id)
    return {"message": "User added to chat"}

@app.get("/user_chats/{user_id}", response_model=list[schemas.Chat])
async def get_chats_by_user(user_id: int):
    chats = await crud.get_chats_by_user(user_id)
    if not chats:
        raise HTTPException(status_code=404, detail="No chats found")
    return chats

@app.get("/messages/{chat_id}", response_model=list[schemas.Message])
async def get_messages_from_chat(chat_id: int, count: int):
    messages = await crud.get_messages_from_chat(chat_id, count)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")
    return messages

@app.post("/messages/", response_model=schemas.Message)
async def send_message_to_chat(message: schemas.MessageCreate):
    return await crud.send_message_to_chat(message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
