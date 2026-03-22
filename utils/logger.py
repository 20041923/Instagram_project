import logging
import os
from datetime import datetime

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 创建日志文件名
log_file = os.path.join(log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 创建logger对象
logger = logging.getLogger('instagram_crawler')

# 导出logger
def get_logger():
    return logger
