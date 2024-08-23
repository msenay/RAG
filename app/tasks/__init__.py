"""Orchestrator module."""
import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker


from app.settings import settings

# init dramatiq broker
broker = RedisBroker(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.dramatiq_redis_db,
    namespace=settings.dramatiq_name_space,
)
dramatiq.set_broker(broker)

redis_conn = redis.Redis(settings.redis_host, port=settings.redis_port, db=settings.embeddings_redis_db)
