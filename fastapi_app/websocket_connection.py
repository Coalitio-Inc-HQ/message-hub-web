# from fastapi import WebSocket, WebSocketDisconnect, HTTPException
# from pydantic import ValidationError
#
# from core.fastapi_app.app import app
# from core.fastapi_app.front_client.front_client_websocket_responses import get_websocket_response_actions
#
# from core import app_config
# from core import ActionDTO
#
# from core.fastapi_app.websocket_manager import websocket_manager
#
#
# @app.websocket(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}")
# async def websocket_endpoint(websocket: WebSocket):  # в будущем авторизация по токену
#     """
#     :param websocket: Websocket
#     :return:
#     """
#     await websocket_manager.connect(websocket)
#     try:
#
#         # Получаем карту методов для ответов фронту
#         response_actions_map = get_websocket_response_actions()
#
#         while True:
#             # Получаем данные от фронта в формате ActionDTO
#             data = await websocket.receive_json()
#             try:
#                 action = ActionDTO(**data)
#                 if response_actions_map.__contains__(action.name):
#                     await response_actions_map[action.name](action.body, websocket)
#                 else:
#                     raise HTTPException(status_code=400,
#                                         detail=f'Неверный заголовок запроса')
#             except ValidationError:
#                 raise HTTPException(status_code=400,
#                                     detail=f'Неверный формат запроса')
#     except WebSocketDisconnect:
#         websocket_manager.disconnect(websocket)
