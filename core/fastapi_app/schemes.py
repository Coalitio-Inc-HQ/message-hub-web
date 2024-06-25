import datetime
from typing import Dict, Callable, Any, TypedDict, List

from pydantic import BaseModel

UserId = int
ChatId = int
MessageId = int
Count = int
ActionName = str


class ActionDTO(BaseModel):
    """
    Экземпляр действия, совершаемого при взаимодействии
    с приложением через вебсокет

    Формат: {name: str, {...тело}}
    """
    name: ActionName
    body: dict


class ChatDTO(BaseModel):
    """
    Экземпляр чата, пришедшего с главного сервера
    """
    id: ChatId
    name: str


class MessageDTO(BaseModel):
    """
    Экземпляр сообщения, в данном формате они хранятся
    на главном сервере
    """
    id: MessageId
    chat_id: ChatId
    sender_id: UserId
    text: str
    date: datetime.datetime | str


class UserDTO(BaseModel):
    id: UserId
    name: str


class ActionsMapTypedDict(TypedDict):
    get_waiting_chats: Callable[[UserId], List[ChatDTO]] | None
    read_chat_by_user: Callable[[UserId, ChatId], ChatDTO] | None
    get_chats_by_user: Callable[[UserId], List[ChatDTO]] | None
    get_messages_from_chat: Callable[[ChatId, Count], List[MessageDTO]] | None
    send_message_to_chat: Callable[[MessageDTO], None] | None
