from redis import Redis
from rq import Queue

from app.core.config import settings

# Global Redis connection and RQ Queue
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
task_queue = Queue(connection=redis_conn) 