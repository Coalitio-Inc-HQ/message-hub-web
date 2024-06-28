from fastapi import WebSocket
from core import ActionDTO


class ConnectionManager:
    """
    Ответственный за отправку всех запросов через вебсокеты.
    Если знаешь кому отправить - send_personal_message,
    если не знаешь - send_personal_response
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

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


websocket_manager = ConnectionManager()
