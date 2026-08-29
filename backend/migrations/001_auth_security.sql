-- 登录安全基础结构：上线前在业务数据库执行一次。
-- 本脚本可重复执行，但执行前仍应完成数据库备份。

-- 部分 Navicat 备份使用 MySQL 8 专属的 utf8mb4_0900_ai_ci。
-- 在 MySQL 5.7 / MariaDB 中导入时，sys_public_user 可能因不支持该排序规则而未能创建。
-- 先以兼容的排序规则补齐基础表，后续安全加固语句才能稳定执行。
CREATE TABLE IF NOT EXISTS sys_public_user (
    id INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
    password VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '加密密码',
    nickname VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '昵称',
    avatar VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '头像URL',
    create_time DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_public_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='公共用户/会员表';

-- 补齐历史账号的审计时间，并让后续注册自动记录创建时间。
UPDATE sys_public_user
SET create_time = CURRENT_TIMESTAMP
WHERE create_time IS NULL;

ALTER TABLE sys_public_user
    MODIFY create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';

-- 后台账号只允许管理员角色；先修复历史空值，再收紧字段约束。
UPDATE sys_user
SET role = 'admin'
WHERE role IS NULL OR TRIM(role) = '';

UPDATE sys_user
SET create_time = CURRENT_TIMESTAMP
WHERE create_time IS NULL;

ALTER TABLE sys_user
    MODIFY role VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        NOT NULL DEFAULT 'admin' COMMENT '角色',
    MODIFY create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';

-- 并发注册必须由数据库唯一索引兜底。下面语句仅在索引不存在时创建。
SET @public_username_index = IF(
    (SELECT COUNT(*) FROM information_schema.STATISTICS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_public_user'
       AND COLUMN_NAME = 'username' AND NON_UNIQUE = 0) = 0,
    'ALTER TABLE sys_public_user ADD UNIQUE KEY uk_public_user_username (username)',
    'SELECT 1'
);
PREPARE stmt FROM @public_username_index;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @admin_username_index = IF(
    (SELECT COUNT(*) FROM information_schema.STATISTICS
     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'sys_user'
       AND COLUMN_NAME = 'username' AND NON_UNIQUE = 0) = 0,
    'ALTER TABLE sys_user ADD UNIQUE KEY uk_user_username (username)',
    'SELECT 1'
);
PREPARE stmt FROM @admin_username_index;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS sys_auth_refresh_token (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    token_hash CHAR(64) NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    account_type ENUM('public', 'admin') NOT NULL,
    persistent TINYINT(1) NOT NULL DEFAULT 0,
    expires_at DATETIME(6) NOT NULL,
    revoked_at DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    last_used_at DATETIME(6) NULL,
    user_agent VARCHAR(255) NULL,
    ip_address VARCHAR(45) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_auth_refresh_token_hash (token_hash),
    KEY idx_auth_refresh_user (account_type, user_id),
    KEY idx_auth_refresh_expiry (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sys_auth_login_attempt (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    account_type ENUM('public', 'admin') NOT NULL,
    event_type ENUM('login', 'register') NOT NULL DEFAULT 'login',
    identity_hash CHAR(64) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    success TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    KEY idx_auth_attempt_limit (event_type, account_type, identity_hash, ip_address, success, created_at),
    KEY idx_auth_attempt_cleanup (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
