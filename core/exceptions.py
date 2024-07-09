class WrongBodyFormatException(Exception):
    pass

class WrongResponseFormatFromMainException(Exception):
    """
    Пришел неверный формат из main_client.
    Либо меняй формат у себя (нежелательно, так как со мной общается
    ещё и фронт), либо уведоми ответственного за главный сервер
    """
    pass

class PlatformRegistrationException(Exception):
    pass

class MainServerWrongUrlException(PlatformRegistrationException):
    """
    Неверный адрес регистрации платформы
    """
    pass

class MainServerWrongJsonFormat(PlatformRegistrationException):
    """
    Неверный формат данных в запросе при регистрации платформы
    """
    pass

class MainServerOfflineException(PlatformRegistrationException):
    """
    Главный сервер выключен или находится вне зоны действия сети
    """

class UserRegistrationException(Exception):
    """
    Ошибка регистрации пользователя на главном сервере
    """
    pass
