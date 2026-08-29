"""数据库连接池事务边界测试。"""

import unittest
from unittest.mock import MagicMock, patch

from utils.database import DBManager


class DatabaseManagerTests(unittest.TestCase):
    def _pool(self):
        cursor = MagicMock()
        connection = MagicMock()
        connection.cursor.return_value = cursor
        pool = MagicMock()
        pool.connection.return_value = connection
        return pool, connection, cursor

    def test_transaction_uses_dbutils_begin_and_commit(self):
        pool, connection, cursor = self._pool()

        with patch("utils.database.get_db_pool", return_value=pool):
            with DBManager(transactional=True) as actual_cursor:
                self.assertIs(actual_cursor, cursor)

        connection.begin.assert_called_once_with()
        connection.commit.assert_called_once_with()
        connection.rollback.assert_not_called()
        connection.close.assert_called_once_with()

    def test_transaction_rolls_back_on_error(self):
        pool, connection, _ = self._pool()

        with self.assertRaisesRegex(RuntimeError, "failure"):
            with patch("utils.database.get_db_pool", return_value=pool):
                with DBManager(transactional=True):
                    raise RuntimeError("failure")

        connection.rollback.assert_called_once_with()
        connection.commit.assert_not_called()
        connection.close.assert_called_once_with()

    def test_autocommit_connection_does_not_require_driver_method(self):
        pool, connection, _ = self._pool()

        with (
            patch("utils.database.get_db_pool", return_value=pool),
            patch.dict("utils.database.Config.DB_CONFIG", {"autocommit": True}),
        ):
            with DBManager():
                pass

        connection.begin.assert_not_called()
        connection.commit.assert_not_called()
        connection.rollback.assert_not_called()
        connection.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
