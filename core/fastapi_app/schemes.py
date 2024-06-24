import datetime

from pydantic import BaseModel

class Chat(BaseModel):
    """
    Экземпляр чата, пришедшего с главного сервера
    """
    id: int
    name: str

class MessageDTO(BaseModel):
    """
    Экземпляр сообщения, в данном формате они хранятся
    на главном сервере
    """
    id: int
    chat_id: int
    sender_id: int
    text: str
    date: datetime.datetime | str
