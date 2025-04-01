import logging

from pydantic import BaseModel, ValidationError
from starlette.websockets import WebSocket

from core import WrongBodyFormatException

from fastapi_app.auth.auth_schemes import ExtUserDTO

from core import ActionResponseDTO, ResponseDTO, ErrorDTO, ActionRequestDTO, RequestDTO

from httpx import HTTPStatusError

from fastapi_app.websocket_manager import websocket_manager

import uuid

logger = logging.getLogger(__name__)


def get_list_of_pydantic_objects(base_model: BaseModel, list_of_elements: list) -> list[BaseModel]:
    return [base_model.model_validate(chat) for chat in list_of_elements]


def check_body_format(keys: list[str]):
    def wrapper(func):
        async def inner(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
            if not all(key in request.obj.body.keys() for key in keys):
                await websocket_manager.send_personal_response(
                    ActionResponseDTO(
                        id=request.id,
                        obj=ResponseDTO(
                            name=request.obj.name,
                            status_code=422,
                            body={},
                            error={
                                "description":  f"Неверный формат body в запросе. Не достает одного из ключей: {','.join(keys)}"
                            }
                        )
                    )
                )
                return None
            result = await func(request, websocket, user)
            return result
        return inner
    return wrapper


def error_catcher(name: str):
    def wrapper(func):
        async def inner(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
            try:
                result = await func(request, websocket, user)
                return result
            except ValueError as err:
                await websocket_manager.send_personal_response(
                    ActionResponseDTO(
                        id=request.id,
                        obj=ResponseDTO(
                            name=request.obj.name,
                            status_code=500,
                            body={},
                            error={
                                "description":  f"Непредвиденная ошибка"
                            }
                        )
                    ),
                    websocket
                )
                logger.error("Непредвиденная ошибка: ", err, request.model_dump_json())
                # action = ActionResponsetDTO(
                #     id=id,
                #     obj=ResponseDTO(
                #         name=name,
                #         status_code=500,
                #         body={},
                #         error=ErrorDTO(error_type="server", error_description="Неверный формат ответа главного сервера")
                #     )
                # )
                # await websocket_manager.send_personal_response(action, websocket)
            except HTTPStatusError as err:
                if 400 <= err.response.status_code < 500:
                    await websocket_manager.send_personal_response(
                        ActionResponseDTO(
                            id=request.id,
                            obj=ResponseDTO(
                                name=request.obj.name,
                                status_code=500,
                                body={},
                                error={
                                    "description":  f"Непредвиденная ошибка"
                                }
                            )
                        ),
                        websocket
                    )
                    logger.error("Непредвиденная ошибка: ", err, request.model_dump_json())
                    # action = ActionResponsetDTO(
                    #     id=id,
                    #     obj = ResponseDTO(
                    #         name=name,
                    #         status_code=422,
                    #         body={},
                    #         error=ErrorDTO(error_type="client", error_description=err.response.text)
                    #     )
                    # )
                    # await websocket_manager.send_personal_response(action, websocket)
                else:
                    await websocket_manager.send_personal_response(
                        ActionResponseDTO(
                            id=request.id,
                            obj=ResponseDTO(
                                name=request.obj.name,
                                status_code=500,
                                body={},
                                error={
                                    "description":  f"Непредвиденная ошибка"
                                }
                            )
                        ),
                        websocket
                    )
                    logger.error("Непредвиденная ошибка: ", err, request.model_dump_json())
                    # action = ActionResponsetDTO(
                    #     id=id,
                    #     obj = ResponseDTO(
                    #         name=name,
                    #         status_code=500,
                    #         body={},
                    #         error=ErrorDTO(error_type="server", error_description="Неизвестная ошибка")
                    #     )
                    # )
                    # await websocket_manager.send_personal_response(action, websocket)
            except WrongBodyFormatException as err:
                await websocket_manager.send_personal_response(
                    ActionResponseDTO(
                        id=request.id,
                        obj=ResponseDTO(
                            name=request.obj.name,
                            status_code=500,
                            body={},
                            error={
                                "description":  f"Непредвиденная ошибка"
                            }
                        )
                    ),
                    websocket
                )
                logger.error("Непредвиденная ошибка: ", err, request.model_dump_json())
                # action = ActionResponsetDTO(
                #     id=id,
                #     obj = ResponseDTO(
                #         name=name,
                #         status_code=422,
                #         body={},
                #         error=ErrorDTO(error_type="client", error_description=str(err))
                #     )
                # )
                # await websocket_manager.send_personal_response(action, websocket)
            except Exception as err:
                await websocket_manager.send_personal_response(
                    ActionResponseDTO(
                        id=request.id,
                        obj=ResponseDTO(
                            name=request.obj.name,
                            status_code=500,
                            body={},
                            error={
                                "description":  f"Непредвиденная ошибка"
                            }
                        )
                    ),
                    websocket
                )
                logger.error("Непредвиденная ошибка: ", err, request.model_dump_json())

                # action = ActionResponsetDTO(
                #     id=id,
                #     obj = ResponseDTO(
                #         name=name,
                #         status_code=500,
                #         body={},
                #         error=ErrorDTO(error_type="server", error_description="Неизвестная ошибка")
                #     )
                # )
                # logger.error("Unknown error: ", e, "body", body)
                # await websocket_manager.send_personal_response(action, websocket)

        return inner

    return wrapper
