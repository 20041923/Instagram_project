from utils.logger import get_logger
import requests
from config import HEADERS

logger = get_logger()

class SetCookiesPool:
    def __init__(self, txt_path):
        self.txt_path = txt_path
        self.cookies_list = self.get_cookies()
        self.cookies = []
        self.valid_cookies = []
        self.cookie_scores = {}

    def get_cookies(self):
        try:
            with open(self.txt_path, "r") as file:
                return [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            logger.critical("cookie文件未找到！")
            return []

    def handle_cookie(self):
        if not self.cookies_list:
            logger.warning("cookie文件为空,没有可用的cookie！")
            return []
        self.cookies = [self.create_cookie(cookie) for cookie in self.cookies_list]
        self.valid_cookies = self.validate_cookies()
        return self.valid_cookies

    @staticmethod
    def create_cookie(cookie_str):
        cookie_list = cookie_str.split('; ')
        # 创建一个空字典来存储键值对
        cookie_dict = {}
        # 遍历列表，将键值对添加到字典中
        for cookie in cookie_list:
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookie_dict[key] = value
        return cookie_dict

    def validate_cookies(self):
        """
        验证cookie的有效性
        """
        valid_cookies = []
        invalid_cookies = []
        
        for i, cookie in enumerate(self.cookies):
            if self.is_cookie_valid(cookie):
                valid_cookies.append(cookie)
                self.cookie_scores[str(cookie)] = 100  # 初始分数
            else:
                invalid_cookies.append(i)  # 记录无效cookie的索引
        
        # 移除无效的cookie
        if invalid_cookies:
            # 倒序删除，避免索引变化影响
            for i in sorted(invalid_cookies, reverse=True):
                if i < len(self.cookies_list):
                    invalid_cookie_str = self.cookies_list[i]
                    logger.info(f"移除无效的cookie: {invalid_cookie_str}")
                    self.cookies_list.pop(i)
            
            # 更新cookie文件
            try:
                with open(self.txt_path, "w") as file:
                    for cookie in self.cookies_list:
                        file.write(cookie + "\n")
                logger.info(f"已从文件中移除{len(invalid_cookies)}个无效cookie")
            except Exception as e:
                logger.error(f"更新cookie文件时出错: {e}")
        
        logger.info(f"验证完成，有效cookie数量: {len(valid_cookies)}")
        return valid_cookies

    def is_cookie_valid(self, cookie):
        """
        检查cookie是否有效
        """
        try:
            response = requests.get(
                'https://www.instagram.com/api/v1/friendships/72483526973/followers/',
                params={'count': '12', 'search_surface': 'follow_list_page'},
                cookies=cookie,
                headers=HEADERS,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"验证cookie时出错: {e},:{cookie}")
            return False

    def remove_cookie(self, target_cookie=""):
        """
        删除指定的 cookie。
        :param target_cookie: 要删除的 cookie 字符串（完整的一行）。
        """
        if not self.cookies_list:
            logger.warning("cookie列表为空，无法删除！")
            return

        # 检查目标 cookie 是否存在
        if target_cookie in self.cookies_list:
            self.cookies_list.remove(target_cookie)
            logger.info(f"已从内存中删除 cookie: {target_cookie}")
        else:
            logger.warning(f"未找到指定的 cookie: {target_cookie}")
            return

        # 更新文本文件
        try:
            with open(self.txt_path, "w") as file:
                for cookie in self.cookies_list:
                    file.write(cookie + "\n")
            logger.info(f"已从文件中删除 cookie: {target_cookie}")
        except Exception as e:
            logger.error(f"更新文件时出错: {e}")

    def get_best_cookie(self):
        """
        获取分数最高的cookie
        """
        if not self.valid_cookies:
            return None
        # 按分数排序，返回分数最高的cookie
        sorted_cookies = sorted(self.valid_cookies, key=lambda x: self.cookie_scores.get(str(x), 0), reverse=True)
        return sorted_cookies[0]

    def update_cookie_score(self, cookie, success):
        """
        更新cookie的分数
        :param cookie: cookie对象
        :param success: 是否成功
        """
        cookie_str = str(cookie)
        if success:
            self.cookie_scores[cookie_str] = self.cookie_scores.get(cookie_str, 0) + 10
        else:
            self.cookie_scores[cookie_str] = max(0, self.cookie_scores.get(cookie_str, 0) - 20)
        # 如果分数过低，从有效cookie列表中移除
        if self.cookie_scores.get(cookie_str, 0) < 50:
            if cookie in self.valid_cookies:
                self.valid_cookies.remove(cookie)
                logger.info(f"cookie分数过低，已从有效列表中移除")


if __name__ == '__main__':
    from urllib.parse import urlencode

    set_cookies_pool = SetCookiesPool(r"E:\Ins_Crawler\cookies.txt")

    # 获取并打印所有 cookies
    cookies = set_cookies_pool.get_cookies()
    print("当前所有 cookies:", cookies)
    cookie = set_cookies_pool.handle_cookie()[0]
    print(cookie)
    cookie_str = "; ".join(f"{key}={value}" for key, value in cookie.items())
    print(cookie_str)
