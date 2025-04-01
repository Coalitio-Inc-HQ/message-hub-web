from fastapi import WebSocket
from core import ActionDTO
from core import logger

class ConnectionManager:
    """
    Ответственный за отправку всех запросов через вебсокеты.
    Если знаешь кому отправить - send_personal_message,
    если не знаешь - send_personal_response
    """

    def __init__(self):
        self.active_connections: dict[list[WebSocket]] = {}
        self.active_chat_connections: dict[set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        # await websocket.accept()
        if user_id in self.active_connections:
            self.active_connections[user_id].append(websocket)
        else:
            self.active_connections[user_id] = [websocket]

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections[user_id].remove(websocket)

        if len(self.active_connections[user_id]) == 0:
            # или найти по WebSocket, user_id
            for chat_connections in self.active_chat_connections:
                self.active_chat_connections[chat_connections].remove(user_id)
            self.active_connections.pop(user_id)

        print(self.active_chat_connections)

    async def connect_user_to_chats(self, user_id: int, chat_ids: list[int]):
        """
        Добавляет соединение пользователя
        в список чата, для прослушивания
        сообщений в нём.
        :param user_id: int
        :param chat_ids: list[int]
        :return:
        """

        if user_id in self.active_connections:
            for chat_id in chat_ids:
                if chat_id in self.active_chat_connections:
                    self.active_chat_connections[chat_id].add(user_id)
                else:
                    self.active_chat_connections[chat_id] = {user_id}

    async def connect_user_to_chat(self, user_id: int, chat_id: int):
        """
        Добавляет соединение пользователя
        в список чата, для прослушивания
        сообщений в нём.
        :param user_id: int
        :param chat_id: list[int]
        :return:
        """
        if user_id in self.active_connections:
            if chat_id in self.active_chat_connections:
                self.active_chat_connections[chat_id].add(user_id)
            else:
                self.active_chat_connections[chat_id] = {user_id}

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    @staticmethod
    async def send_personal_response(action: ActionDTO, websocket: WebSocket):
        await websocket.send_json(action.model_dump(mode="json"))

    async def broadcast(self, action: ActionDTO):
        """
        Отправляет сообщение всем активным клиентам.
        На данный момент используется при получении уведомления
        с главного сервера, когда нет информации о том
        вебсокет-соединении, по которому нужно отправить.

        :param action: ActionDTO
        :return:
        """

        for key, user_connection in self.active_connections.items():
            for connection in user_connection:
                await connection.send_json(action.model_dump(mode="json"))

    async def send_to_chat(self, action: ActionDTO, chat_id: int):
        """
        Отправляет сообщение всем активным клиентам чата.

        :param action: ActionDTO
        :param chat_id: int
        :return:
        """

        if chat_id in self.active_chat_connections:
            for user_connection_id in self.active_chat_connections[chat_id]:
                for connection in self.active_connections[user_connection_id]:
                    await connection.send_json(action.model_dump(mode="json"))

    async def send_to_user_by_user_id(self, action: ActionDTO, user_id: int):
        """
        Отправляет сообщение пользователю.

        :param action: ActionDTO
        :param user_id: int
        :return:
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(action.model_dump(mode="json"))
                except Exception as err:
                    logger.error(f"Ошибка отправки сообщения пользователю {user_id}", err)

websocket_manager = ConnectionManager()
