import redis.asyncio as redis
from core.config_reader import config

redis = redis.Redis(
    host=config.REDIS_HOST, 
    port=config.REDIS_PORT,
    username=config.REDIS_USERNAME,
    password=config.REDIS_PASSWORD,
    ssl=config.REDIS_USE_SSL,
    decode_responses=True)