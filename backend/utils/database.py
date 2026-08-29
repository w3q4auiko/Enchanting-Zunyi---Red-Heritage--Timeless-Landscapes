"""数据库连接池与会话管理模块。

该模块集中管理连接池、事务边界与查询执行路径，为旅游信息系统的
景区、美食、路线等核心数据提供稳定的访问能力。
"""

import logging

import pymysql
from dbutils.pooled_db import PooledDB

from config import Config

_POOL = None


def get_db_pool():
    """获取全局连接池实例。

    通过惰性初始化保持启动成本可控，并在运行期复用连接以提升吞吐。

    Args:
        None.

    Returns:
        PooledDB: 数据库连接池实例。
    """
    global _POOL
    if _POOL is None:
        db = Config.DB_CONFIG
        _POOL = PooledDB(
            creator=pymysql,
            maxconnections=db.get("pool_size", 20),
            mincached=1,
            maxcached=max(2, db.get("pool_size", 20)),
            blocking=True,
            host=db["host"],
            port=db["port"],
            user=db["user"],
            password=db["password"],
            database=db["database"],
            charset="utf8mb4",
            autocommit=db.get("autocommit", True),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=db.get("connect_timeout", 5),
            read_timeout=db.get("read_timeout", 10),
            write_timeout=db.get("write_timeout", 10),
            ping=1,
        )
    return _POOL


class DBManager:
    """数据库会话上下文管理器。

    通过上下文协议统一管理连接与游标生命周期，并在异常场景下
    保证事务边界的收敛与资源回收。
    """

    def __init__(self, transactional=False):
        """初始化会话容器状态。

        Args:
            None.

        Returns:
            None.
        """
        self.conn = None
        self.cursor = None
        self.transactional = transactional

    def __enter__(self):
        """进入上下文并获取连接资源。

        Args:
            None.

        Returns:
            pymysql.cursors.Cursor: 字典游标实例。
        """
        pool = get_db_pool()
        self.conn = pool.connection()
        if self.transactional:
            # DBUtils 的连接池代理公开 begin/commit/rollback，但不会透传
            # PyMySQL 的 autocommit 方法；显式开启事务可同时兼容两层连接。
            self.conn.begin()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文并收敛事务。

        Args:
            exc_type (type | None): 异常类型。
            exc_val (BaseException | None): 异常实例。
            exc_tb (traceback | None): 异常回溯。

        Returns:
            None.
        """
        try:
            should_finalize = self.transactional or not Config.DB_CONFIG.get("autocommit", True)
            if self.conn and should_finalize:
                if exc_type:
                    self.conn.rollback()
                else:
                    self.conn.commit()
        except Exception as db_err:
            logging.exception("Transaction finalize failed: %s", db_err)
            if exc_type is None:
                raise
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()


def query_all(sql, args=None):
    """执行批量查询并返回结果集。

    Args:
        sql (str): 参数化 SQL 语句。
        args (tuple | list | None): SQL 参数。

    Returns:
        list[dict]: 查询结果列表。
    """
    with DBManager() as cursor:
        cursor.execute(sql, args)
        return cursor.fetchall()


def query_one(sql, args=None):
    """执行单条查询并返回首条结果。

    Args:
        sql (str): 参数化 SQL 语句。
        args (tuple | list | None): SQL 参数。

    Returns:
        dict | None: 首条命中记录，若无结果返回 None。
    """
    with DBManager() as cursor:
        cursor.execute(sql, args)
        return cursor.fetchone()


def execute(sql, args=None):
    """执行数据变更语句。

    Args:
        sql (str): 参数化 SQL 语句。
        args (tuple | list | None): SQL 参数。

    Returns:
        int: 受影响行数。
    """
    with DBManager() as cursor:
        affected = cursor.execute(sql, args)
        return affected
