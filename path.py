import os
import sys
import time
from colorama import Fore, init

init(autoreset=True)  # 自动重置样式


def check_path(all_path):
    """检查资源路径是否存在"""
    if not os.path.exists(all_path):
        print(Fore.YELLOW + f"{all_path}不存在，请放入该目录下！")
        print(Fore.BLUE + "正在关闭程序...")
        for i in range(10):
            print(Fore.GREEN + f"程序将在{i + 1}秒后关闭...")
            time.sleep(1)
        return False
    return True


base_path = os.path.abspath(".")
data_base_path = os.path.join(base_path, "data")