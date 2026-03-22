import threading
import queue
from task_queue.task_queue import task_queue
from db.dao import insert_followers
from config import BATCH_SIZE

def db_worker():
    batch = []
    while True:
        try:
            # 等待任务，超时时间为5秒
            data = task_queue.get(timeout=5)
            batch.append(data)

            if len(batch) >= BATCH_SIZE:
                insert_followers(batch)
                batch.clear()

            task_queue.task_done()
        except queue.Empty:
            # 当队列为空且有未处理的任务时，处理剩余任务
            if batch:
                insert_followers(batch)
                batch.clear()
            continue


def start_db_workers(num=2):
    for _ in range(num):
        t = threading.Thread(target=db_worker, daemon=True)
        t.start()