# 导入必要的模块
import sys  # 导入系统模块
import requests  # 导入网络请求模块
import random  # 导入随机模块
import time  # 导入时间模块
from threading import Lock  # 导入锁模块
from task_queue.task_queue import task_queue  # 导入任务队列
from db.dao import update_progress  # 导入进度更新函数
from config import HEADERS, USE_PROXY, MAX_ATTEMPTS  # 导入配置参数
from utils.tools import get_proxies, check_cookie, remove_cookie  # 导入工具函数
from utils.logger import get_logger  # 导入日志工具

# 获取logger对象
logger = get_logger()

# 复制请求头
headers = HEADERS.copy()


class Crawler:
    """
    爬虫类，负责爬取Instagram用户的粉丝数据
    """

    def __init__(self, user_id_file, proxies_file, cookies_file, set_proxies_pool, set_cookies_pool):
        """
        初始化爬虫
        :param user_id_file: 用户ID文件路径
        :param proxies_file: 代理文件路径
        :param cookies_file: Cookie文件路径
        :param set_proxies_pool: 代理池对象
        :param set_cookies_pool: Cookie池对象
        """
        self.user_id_file = user_id_file  # 用户ID文件路径
        self.max_attempts = MAX_ATTEMPTS  # 最大重试次数
        self.use_proxy = USE_PROXY  # 是否使用代理
        self.lock = Lock()  # 线程锁
        self.proxies_file = proxies_file  # 代理文件路径
        self.cookies_file = cookies_file  # Cookie文件路径
        self.proxies_pool = set_proxies_pool.proxies  # 代理池
        self.cookies_pool = set_cookies_pool.valid_cookies  # 有效Cookie池
        self.set_cookies_pool = set_cookies_pool  # Cookie池对象
        self.session = requests.Session()  # 创建会话对象，减少连接开销
        self.session.headers.update(headers)  # 更新会话头

    def _remove_user_id(self, user_id):
        """
        从文件中移除已完成的用户ID
        :param user_id: 用户ID
        """
        with self.lock:
            with open(self.user_id_file, "r", encoding="utf-8") as f:
                user_ids = [line.strip() for line in f if line.strip()]
            if user_id in user_ids:
                user_ids.remove(user_id)
                with open(self.user_id_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(user_ids))
                logger.info(f"已从文件中移除 user_id: {user_id}")

    def crawl_user(self, user_id):
        """
        爬取指定用户的粉丝数据
        :param user_id: 用户ID
        :return: (user_id, success) 元组
        """
        max_id = 0  # 分页标记
        logger.info(f"开始获取{user_id}的粉丝数据...")
        url = f"https://www.instagram.com/api/v1/friendships/{user_id}/followers/"  # API地址

        while True:
            attempt = 0  # 重试次数
            # 获取最佳Cookie
            cookies = self.set_cookies_pool.get_best_cookie()
            if not cookies and self.cookies_pool:
                cookies = random.choice(self.cookies_pool)
            logger.debug(f"当前cookies: {cookies}")

            while attempt < self.max_attempts:
                # 构建请求参数
                params = {
                    'count': '12',  # 每次获取12个粉丝
                    'max_id': str(max_id),  # 分页标记
                    'search_surface': 'follow_list_page',  # 搜索表面
                }
                proxies = None
                if self.use_proxy:
                    proxies = get_proxies(self)
                try:
                    # 发送请求
                    resp = self.session.get(url, params=params,
                                            cookies=cookies,
                                            proxies=proxies
                                            ).json()
                    # 请求成功，更新cookie分数
                    self.set_cookies_pool.update_cookie_score(cookies, True)
                except requests.exceptions.RequestException as e:
                    logger.error(f"请求失败，正在重试... 错误信息：{e}")
                    # 请求失败，更新cookie分数
                    self.set_cookies_pool.update_cookie_score(cookies, False)
                    attempt += 1
                    if attempt == self.max_attempts:
                        # 检查cookie是否失效
                        cookies_status = check_cookie(cookies, get_proxies(self))
                        if cookies_status == "fail":
                            cookie_str = "; ".join(f"{key}={value}" for key, value in cookies.items())
                            logger.error(f"cookie失效，删除cookie{cookie_str}")
                            with self.lock:
                                remove_cookie(self.cookies_file, cookie_str)
                                if cookies in self.cookies_pool:
                                    self.cookies_pool.remove(cookies)
                                if not self.cookies_pool:
                                    logger.critical("cookie池已全部失效，结束程序！")
                                    time.sleep(10)
                                    sys.exit()
                        logger.error(f"重试次数已用完，无法获取{user_id}数据。")
                        return user_id, False
                    time.sleep(5)
                    continue
                try:
                    users = resp['users']
                except KeyError:
                    logger.error(f"{user_id}api返回数据为空")
                    # cookie失效，更新分数
                    self.set_cookies_pool.update_cookie_score(cookies, False)
                    cookie_str = "; ".join(f"{key}={value}" for key, value in cookies.items())
                    logger.error(f"cookie失效，删除cookie:{cookie_str}")
                    with self.lock:
                        remove_cookie(self.cookies_file, cookie_str)
                        if cookies in self.cookies_pool:
                            self.cookies_pool.remove(cookies)
                        if not self.cookies_pool:
                            logger.critical("cookie池已全部失效，结束程序！")
                            time.sleep(10)
                            sys.exit()
                    # 获取新的cookie
                    cookies = self.set_cookies_pool.get_best_cookie()
                    if not cookies and self.cookies_pool:
                        cookies = random.choice(self.cookies_pool)
                    continue
                # 处理获取到的粉丝数据
                logger.info(f"获取到{len(users)}个粉丝")
                for u in users:
                    # 将粉丝数据放入任务队列
                    task_queue.put((
                        user_id,
                        u["id"],
                        u["username"],
                        u["profile_pic_url"]
                    ))
                # 检查是否有更多数据
                big_list = resp.get('big_list', False)
                next_max_id = resp.get('next_max_id', None)
                if big_list and next_max_id:
                    if next_max_id != max_id:  # 如果 next_max_id 改变，更新 max_id 并继续请求
                        max_id = next_max_id
                        update_progress(user_id, max_id, 0)
                        # 随机延迟，避免被封
                        time.sleep(random.uniform(0.5, 1.5))
                        logger.info(f"{user_id}:max_id不同-->{max_id}")
                        logger.debug(f"下一页max_id: {next_max_id}")
                    else:
                        logger.info(f"{user_id}max_id相同，没有更多粉丝数据，停止请求。")
                        return user_id, True
                else:
                    logger.info(f"{user_id}的粉丝数据获取完成！")
                    self._remove_user_id(user_id)  # 数据抓取完毕，移除 user_id
                    return user_id, True
                break
