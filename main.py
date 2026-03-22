# 导入必要的模块
from core.scheduler import run  # 导入调度器
from task_queue.task_queue import task_queue  # 导入任务队列
from core.db_worker import start_db_workers  # 导入数据库工作线程启动函数
from path import *  # 导入路径相关函数
from utils.logger import get_logger  # 导入日志工具
import sys  # 导入系统模块

# 获取logger对象
logger = get_logger()


def load_list(path):
    """
    从文件中加载列表数据
    :param path: 文件路径
    :return: 列表数据
    """
    with open(path, "r") as f:
        return [i.strip() for i in f if i.strip()]


if __name__ == "__main__":
    # 构建文件路径
    proxies_file = os.path.join(data_base_path, "proxies.txt")  # 代理文件路径
    cookies_file = os.path.join(data_base_path, "cookies.txt")  # Cookie文件路径
    user_id_file = os.path.join(data_base_path, "user_ids.txt")  # 用户ID文件路径
    
    # 检查文件是否存在
    for i in [user_id_file, cookies_file, proxies_file]:
        if check_path(i):
            logger.info(f"已获取{i}")
        else:
            logger.critical(f"文件不存在: {i}")
            sys.exit()
    
    # 启动数据库线程
    start_db_workers(3)  # 启动3个数据库工作线程
    logger.info("已启动")
    
    # 启动爬虫
    run(user_id_file, proxies_file, cookies_file)

    # 等待队列完成
    task_queue.join()

    logger.info("全部完成")
