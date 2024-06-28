import logging

from core.config_reader import config as app_config

from core.fastapi_app.schemes import *

from core.exceptions import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('core_logger')
