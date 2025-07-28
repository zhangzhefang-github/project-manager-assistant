from app.services.task_queue import redis_conn
from rq import Worker

if __name__ == '__main__':
    # Create a worker that listens on the default queue
    worker = Worker(['default'], connection=redis_conn)
    print("RQ worker started. Listening for tasks...")
    worker.work() 