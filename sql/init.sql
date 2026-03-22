CREATE TABLE followers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    follower_id VARCHAR(50),
    follower_name VARCHAR(100),
    follower_pic TEXT,
    UNIQUE KEY uniq_user_follower (user_id, follower_id)
);

CREATE TABLE user_progress (
    user_id VARCHAR(50) PRIMARY KEY,
    max_id VARCHAR(100),
    status TINYINT DEFAULT 0
);