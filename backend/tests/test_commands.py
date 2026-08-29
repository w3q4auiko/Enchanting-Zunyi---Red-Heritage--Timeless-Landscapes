"""管理员运维命令测试。"""

import unittest
from unittest.mock import MagicMock, patch

from flask import Flask
from werkzeug.security import check_password_hash

from commands import register_commands


class AdminCommandTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        register_commands(self.app)

    def test_reset_admin_password_hashes_password_and_revokes_sessions(self):
        cursor = MagicMock()
        manager = MagicMock()
        manager.__enter__.return_value = cursor

        with (
            patch("commands.query_one", return_value={"id": 7}),
            patch("commands.DBManager", return_value=manager) as db_manager,
        ):
            result = self.app.test_cli_runner().invoke(
                args=["reset-admin-password", "--username", "admin"],
                input="SafePass9!\nSafePass9!\n",
            )

        self.assertEqual(result.exit_code, 0, result.output)
        db_manager.assert_called_once_with(transactional=True)
        password_params = cursor.execute.call_args_list[0].args[1]
        self.assertTrue(check_password_hash(password_params[0], "SafePass9!"))
        self.assertEqual(password_params[1], 7)
        self.assertEqual(cursor.execute.call_args_list[1].args[1], (7,))
        self.assertIn("现有登录会话已撤销", result.output)


if __name__ == "__main__":
    unittest.main()
