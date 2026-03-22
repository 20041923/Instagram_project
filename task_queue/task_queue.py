from queue import Queue
from config import QUEUE_SIZE

task_queue = Queue(maxsize=QUEUE_SIZE)
