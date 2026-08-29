-- 内容数据导入兼容迁移。
--
-- 用途：修复 Excel 导入工具将长文本列错误推断为短 VARCHAR 后产生的
-- “1406 - Data too long for column”错误。脚本只调整字段类型，不删除数据。
-- 执行前仍建议备份数据库，并确保已选择 zunyi_tourism 数据库。

ALTER DATABASE zunyi_tourism
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

ALTER TABLE sys_attraction
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY description LONGTEXT NULL,
    MODIFY tips LONGTEXT NULL,
    MODIFY banner_desc LONGTEXT NULL;

ALTER TABLE sys_food
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY description LONGTEXT NULL,
    MODIFY tips LONGTEXT NULL,
    MODIFY banner_desc LONGTEXT NULL;

ALTER TABLE sys_food_street
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY description LONGTEXT NULL;

ALTER TABLE sys_region
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    MODIFY description LONGTEXT NULL;
