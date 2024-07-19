from fastapi import WebSocket
from core import ActionDTO, ActionDTOOut


class ConnectionManager:
    """
    Ответственный за отправку всех запросов через вебсокеты.
    Если знаешь кому отправить - send_personal_message,
    если не знаешь - send_personal_response
    """

    def __init__(self):
        self.active_connections: dict[WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.pop(user_id)

    @staticmethod
    async def send_personal_response(action: ActionDTOOut, websocket: WebSocket):
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
            await self.active_connections[connection].send_json(action.model_dump())


websocket_manager = ConnectionManager()
