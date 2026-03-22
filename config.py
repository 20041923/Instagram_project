from utils.logger import get_logger

logger = get_logger()

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "crawler",
    "charset": "utf8mb4"
}
USE_PROXY = False  # ✅ 是否启用代理（改这里就行）
MAX_WORKERS = 10
MAX_ATTEMPTS = 10
QUEUE_SIZE = 10000
BATCH_SIZE = 50
COOKIE_THREAD_RATIO = 0.8  # 线程数与cookie数的最大比例
HEADERS = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.instagram.com/',
    'sec-ch-prefers-color-scheme': 'dark',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="137.0.7151.120", "Chromium";v="137.0.7151.120", "Not/A)Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-csrftoken': 'CnbTqLVF8iKVynnJi4zDUYQbyFXsS4F0',
    'x-ig-app-id': '936619743392459',
    'x-requested-with': 'XMLHttpRequest',
}


def validate_config():
    """
    验证配置项的有效性
    """
    errors = []
    
    # 验证数据库配置
    if not isinstance(DB_CONFIG, dict):
        errors.append("DB_CONFIG must be a dictionary")
    else:
        required_db_keys = ["host", "user", "password", "database"]
        for key in required_db_keys:
            if key not in DB_CONFIG:
                errors.append(f"DB_CONFIG missing required key: {key}")
    
    # 验证布尔值配置
    if not isinstance(USE_PROXY, bool):
        errors.append("USE_PROXY must be a boolean")
    
    # 验证数值配置
    numeric_configs = {
        "MAX_WORKERS": MAX_WORKERS,
        "MAX_ATTEMPTS": MAX_ATTEMPTS,
        "QUEUE_SIZE": QUEUE_SIZE,
        "BATCH_SIZE": BATCH_SIZE
    }
    
    for name, value in numeric_configs.items():
        if not isinstance(value, int):
            errors.append(f"{name} must be an integer")
        elif value <= 0:
            errors.append(f"{name} must be greater than 0")
    
    # 验证COOKIE_THREAD_RATIO
    if not isinstance(COOKIE_THREAD_RATIO, (int, float)):
        errors.append("COOKIE_THREAD_RATIO must be a number")
    elif COOKIE_THREAD_RATIO <= 0 or COOKIE_THREAD_RATIO > 1:
        errors.append("COOKIE_THREAD_RATIO must be between 0 and 1")
    
    # 验证HEADERS
    if not isinstance(HEADERS, dict):
        errors.append("HEADERS must be a dictionary")
    else:
        required_headers = ["user-agent", "x-ig-app-id"]
        for header in required_headers:
            if header not in HEADERS:
                errors.append(f"HEADERS missing required header: {header}")
    
    # 输出验证结果
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        logger.critical("Configuration validation failed. Please check your config.py file.")
        return False
    else:
        logger.info("Configuration validation passed.")
        return True


# 自动验证配置
validate_config()