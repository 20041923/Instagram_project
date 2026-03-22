import pymysql
from dbutils.pooled_db import PooledDB
from config import DB_CONFIG


def init_database():
    """
    初始化数据库（不存在就创建）
    """
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        charset="utf8mb4"
    )

    cursor = conn.cursor()

    # 创建数据库
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARSET utf8mb4;")

    conn.commit()
    cursor.close()
    conn.close()


def init_tables():
    """
    初始化表（不存在就创建）
    """
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # followers 表
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS followers
                   (
                       id            BIGINT AUTO_INCREMENT PRIMARY KEY,
                       user_id       VARCHAR(50),
                       follower_id   VARCHAR(50),
                       follower_name VARCHAR(100),
                       follower_pic  TEXT,
                       UNIQUE KEY uniq_user_follower (user_id, follower_id)
                   );
                   """)

    # user_progress 表
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS user_progress
                   (
                       user_id VARCHAR(50) PRIMARY KEY,
                       max_id  VARCHAR(100),
                       status  TINYINT DEFAULT 0
                   );
                   """)

    conn.commit()
    cursor.close()
    conn.close()


# 初始化
init_database()
init_tables()

# ===== 连接池 =====
pool = PooledDB(
    creator=pymysql,
    maxconnections=10,
    mincached=3,
    blocking=True,
    **DB_CONFIG
)


def get_conn():
    return pool.connection()
