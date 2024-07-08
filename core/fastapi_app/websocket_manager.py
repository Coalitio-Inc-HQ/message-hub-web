from fastapi import WebSocket
from core import ActionDTO


class ConnectionManager:
    """
    Ответственный за отправку всех запросов через вебсокеты.
    Если знаешь кому отправить - send_personal_message,
    если не знаешь - send_personal_response
    """

    def __init__(self):
        self.active_connections: dict[WebSocket] = {}
        self.active_chat_connections: dict[list[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: int):
        # или найти по WebSocket, user_id
        for chat_connections in self.active_chat_connections:
            chat_connections.remove(user_id)
        self.active_connections.pop(user_id)

    async def connect_user_to_chats(self, user_id: int, chat_ids: list[int]):
        """
        Добавляет соедение пользователя
        в список чата, для прослушивания
        сообщений в нём.
        :param user_id: int
        :param chat_ids: list[int]
        :return:
        """

        for chat_id in chat_ids:
            if self.active_chat_connections[chat_id]:
                self.active_chat_connections[chat_id].append(user_id)
            else:
                self.active_chat_connections[chat_id] = [user_id]

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    @staticmethod
    async def send_personal_response(action: ActionDTO, websocket: WebSocket):
        await websocket.send_json(action.model_dump())

    async def broadcast(self, action: ActionDTO):
        """
        Отправляет сообщение всем активным клиентам.
        На данный момент используется при получении уведомления
        с главного сервера, когда нет информации о том
        вебсокет-соединении, по которому нужно отправить.

        :param action: ActionDTO
        :return:
        """

        for connection in self.active_connections:
            await connection.send_json(action.model_dump())

    async def send_to_chat(self, action: ActionDTO, chat_id: int):
        """
        Отправляет сообщение всем активным клиентам чата.

        :param action: ActionDTO
        :param chat_id: int
        :return:
        """

        if self.active_chat_connections[chat_id]:
            for connection_id in self.active_chat_connections[chat_id]:
                await self.active_connections[connection_id].send_json(action.model_dump())


websocket_manager = ConnectionManager()
