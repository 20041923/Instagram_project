from db.mysql import get_conn

def insert_followers(data):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT IGNORE INTO followers 
            (user_id, follower_id, follower_name, follower_pic)
            VALUES (%s, %s, %s, %s)
            """
            cursor.executemany(sql, data)
        conn.commit()
    finally:
        conn.close()


def update_progress(user_id, max_id, status):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO user_progress (user_id, max_id, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            max_id=%s, status=%s
            """
            cursor.execute(sql, (user_id, max_id, status, max_id, status))
        conn.commit()
    finally:
        conn.close()