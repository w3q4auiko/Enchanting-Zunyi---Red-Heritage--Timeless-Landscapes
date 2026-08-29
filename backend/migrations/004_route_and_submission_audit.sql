-- 补齐旅游路线业务表，并为用户投稿保留提交人和提交时间。
-- 本脚本可重复执行，不会覆盖已有业务数据。

CREATE TABLE IF NOT EXISTS sys_route (
    id INT NOT NULL AUTO_INCREMENT,
    category VARCHAR(50) NULL DEFAULT '山野徒步',
    title VARCHAR(100) NOT NULL,
    difficulty TINYINT UNSIGNED NULL DEFAULT 1,
    distance_km DECIMAL(8, 2) NULL DEFAULT 0,
    duration_hours DECIMAL(6, 2) NULL DEFAULT 0,
    climb_meters INT NULL DEFAULT 0,
    route_type VARCHAR(30) NULL DEFAULT '环线',
    start_point VARCHAR(255) NULL DEFAULT NULL,
    address VARCHAR(255) NULL DEFAULT NULL,
    description LONGTEXT NULL,
    tips TEXT NULL,
    image_url VARCHAR(255) NULL DEFAULT NULL,
    banner_url VARCHAR(255) NULL DEFAULT NULL,
    latitude DECIMAL(10, 6) NULL DEFAULT NULL,
    longitude DECIMAL(10, 6) NULL DEFAULT NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    submitted_by INT NULL DEFAULT NULL COMMENT '投稿用户ID',
    submitted_at DATETIME NULL DEFAULT NULL COMMENT '投稿时间',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_route_status (status),
    KEY idx_route_submitted_by (submitted_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='旅游路线表';

SET @add_attraction_submitter = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_attraction'
       AND COLUMN_NAME = 'submitted_by') = 0,
    'ALTER TABLE sys_attraction ADD COLUMN submitted_by INT NULL DEFAULT NULL COMMENT ''投稿用户ID''',
    'SELECT 1'
);
PREPARE stmt FROM @add_attraction_submitter;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @add_attraction_submitted_at = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_attraction'
       AND COLUMN_NAME = 'submitted_at') = 0,
    'ALTER TABLE sys_attraction ADD COLUMN submitted_at DATETIME NULL DEFAULT NULL COMMENT ''投稿时间''',
    'SELECT 1'
);
PREPARE stmt FROM @add_attraction_submitted_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @add_food_submitter = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_food'
       AND COLUMN_NAME = 'submitted_by') = 0,
    'ALTER TABLE sys_food ADD COLUMN submitted_by INT NULL DEFAULT NULL COMMENT ''投稿用户ID''',
    'SELECT 1'
);
PREPARE stmt FROM @add_food_submitter;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @add_food_submitted_at = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_food'
       AND COLUMN_NAME = 'submitted_at') = 0,
    'ALTER TABLE sys_food ADD COLUMN submitted_at DATETIME NULL DEFAULT NULL COMMENT ''投稿时间''',
    'SELECT 1'
);
PREPARE stmt FROM @add_food_submitted_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
