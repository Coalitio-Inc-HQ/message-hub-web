class WrongBodyFormatException(Exception):
    pass

class WrongResponseFormatFromMainException(Exception):
    """
    Пришел неверный формат из main.
    Либо меняй формат у себя (нежелательно, так как со мной общается
    ещё и фронт), либо уведоми ответственного за главный сервер
    """
    pass
