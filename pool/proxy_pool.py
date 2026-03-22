from utils.logger import get_logger
import requests
from config import HEADERS

logger = get_logger()

class SetProxiesPool:
    def __init__(self, txt_path):
        self.txt_path = txt_path
        self.proxies_list = self.get_proxies()
        self.proxies = []

    def get_proxies(self):
        try:
            with open(self.txt_path, "r") as file:
                return [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            logger.critical("代理文件未找到！")
            return []

    def handle_proxy(self):
        if not self.proxies_list:
            logger.warning("代理文件为空,没有可用的代理！")
            return []

        # 验证并创建代理
        valid_proxies = []
        invalid_proxies = []
        
        for i, proxy_str in enumerate(self.proxies_list):
            try:
                proxy = self.create_proxy(proxy_str)
                if self.is_proxy_valid(proxy):
                    valid_proxies.append(proxy)
                else:
                    invalid_proxies.append(i)
            except Exception as e:
                logger.error(f"创建代理时出错: {e}")
                invalid_proxies.append(i)
        
        # 移除无效的代理
        if invalid_proxies:
            # 倒序删除，避免索引变化影响
            for i in sorted(invalid_proxies, reverse=True):
                if i < len(self.proxies_list):
                    invalid_proxy_str = self.proxies_list[i]
                    logger.info(f"移除无效的代理: {invalid_proxy_str}")
                    self.proxies_list.pop(i)
            
            # 更新代理文件
            try:
                with open(self.txt_path, "w") as file:
                    for proxy in self.proxies_list:
                        file.write(proxy + "\n")
                logger.info(f"已从文件中移除{len(invalid_proxies)}个无效代理")
            except Exception as e:
                logger.error(f"更新代理文件时出错: {e}")
        
        self.proxies = valid_proxies
        logger.info(f"验证完成，有效代理数量: {len(valid_proxies)}")
        return self.proxies

    def is_proxy_valid(self, proxy):
        """
        检查代理是否可用
        """
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            # 使用更简单的网址检测代理，减少超时时间
            response = requests.get(
                'http://www.google.com/generate_204',  # Google的空响应服务，速度快
                proxies=proxies,
                timeout=5  # 减少超时时间，提高验证速度
            )
            return response.status_code == 204
        except Exception as e:
            # 只记录关键错误，避免日志过多
            logger.debug(f"验证代理时出错: {e}")
            return False

    @staticmethod
    def create_proxy(proxy):
        proxy_host, proxy_port, proxy_user, proxy_pass = proxy.split(":")
        pconfig = {
            'proxyUser': proxy_user,
            'proxyPass': proxy_pass,
            'proxyHost': proxy_host,
            'proxyPort': proxy_port
        }
        return "http://{}:{}@{}:{}".format(pconfig['proxyUser'], pconfig['proxyPass'], pconfig['proxyHost'],
                                           pconfig['proxyPort'])


if __name__ == '__main__':
    set_proxies_pool = SetProxiesPool(r"E:\Ins_Crawler\data\proxies.txt")
    proxies = set_proxies_pool.handle_proxy()
    print(proxies)
