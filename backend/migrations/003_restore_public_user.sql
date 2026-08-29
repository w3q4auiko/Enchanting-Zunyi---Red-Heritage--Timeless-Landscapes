-- 修复重建数据库后缺失的公众用户表。
--
-- 背景：旧 Navicat 备份中该表使用 utf8mb4_0900_ai_ci，
-- 该排序规则仅受 MySQL 8 支持，在 MySQL 5.7 / MariaDB 中会导致建表失败。
-- 本迁移可重复执行，不会删除或覆盖已有用户数据。

CREATE TABLE IF NOT EXISTS sys_public_user (
    id INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
    password VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '加密密码',
    nickname VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '昵称',
    avatar VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '头像URL',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_public_user_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='公共用户/会员表';
