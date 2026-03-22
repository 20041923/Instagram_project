# 导入必要的模块
from concurrent.futures import ThreadPoolExecutor  # 导入线程池
from config import MAX_WORKERS, COOKIE_THREAD_RATIO  # 导入配置参数
from core.crawler import Crawler  # 导入爬虫类
from pool.cookie_pool import SetCookiesPool  # 导入Cookie池类
from pool.proxy_pool import SetProxiesPool  # 导入代理池类
from utils.logger import get_logger  # 导入日志工具

# 获取logger对象
logger = get_logger()


def run(user_id_file, proxies_file, cookies_file):
    """
    运行爬虫任务
    :param user_id_file: 用户ID文件路径
    :param proxies_file: 代理文件路径
    :param cookies_file: Cookie文件路径
    """
    # 初始化Cookie池
    set_cookies_pool = SetCookiesPool(cookies_file)
    cookies_pool = set_cookies_pool.handle_cookie()
    
    # 初始化代理池
    set_proxies_pool = SetProxiesPool(proxies_file)
    proxies_pool = set_proxies_pool.handle_proxy()
    
    # 初始化爬虫
    crawler = Crawler(user_id_file, proxies_file, cookies_file, set_proxies_pool, set_cookies_pool)
    
    # 读取用户ID列表
    with open(user_id_file, "r", encoding="utf-8") as f:
        user_ids = [line.strip().split(",")[0] for line in f if line.strip()]
    
    # 根据cookie数量和比例计算实际线程数
    cookie_count = len(cookies_pool)
    if cookie_count == 0:
        logger.critical("没有可用的cookie，无法执行爬虫任务")
        return
    
    # 计算最大允许的线程数
    max_allowed_workers = int(cookie_count * COOKIE_THREAD_RATIO)
    # 确保至少有一个线程
    max_allowed_workers = max(1, max_allowed_workers)
    # 不超过配置的最大线程数
    actual_workers = min(MAX_WORKERS, max_allowed_workers)
    
    logger.info(f"Cookie数量: {cookie_count}, 配置的最大线程数: {MAX_WORKERS}, 计算的最大线程数: {max_allowed_workers}, 实际使用线程数: {actual_workers}")
    
    # 使用线程池执行爬虫任务
    with ThreadPoolExecutor(max_workers=actual_workers) as executor:
        for uid in user_ids:
            executor.submit(crawler.crawl_user, uid)
    
    logger.info("所有任务完成！")
