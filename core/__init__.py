from core.config_reader import config as app_config
from core.fastapi_app.schemes import *
from core.fastapi_app.websocket_connection_manager import manager as websocket_manager
from core.exceptions import *
# достучаться до этих импортов можно в любом файле внутри core
# по импорту from core import *
