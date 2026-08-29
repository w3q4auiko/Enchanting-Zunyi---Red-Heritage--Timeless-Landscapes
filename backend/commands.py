"""安全的运维命令。"""

import click
import pymysql
from flask import Flask
from werkzeug.security import generate_password_hash

from utils.auth_validation import (
    ValidationError,
    validate_nickname,
    validate_password,
    validate_username,
)
from utils.database import DBManager, query_one


def register_commands(app: Flask) -> None:
    """注册仅能从服务器终端执行的管理员运维命令。"""

    @app.cli.command("create-admin")
    @click.option("--username", prompt="管理员账号")
    @click.option("--nickname", prompt="管理员昵称")
    @click.password_option(confirmation_prompt=True)
    def create_admin(username: str, nickname: str, password: str) -> None:
        """创建首个或应急管理员账号。"""
        try:
            username = validate_username(username)
            nickname = validate_nickname(nickname)
            password = validate_password(password, username)
        except ValidationError as exc:
            raise click.ClickException(exc.message) from exc

        if query_one("SELECT id FROM sys_user WHERE username = %s", (username,)):
            raise click.ClickException("管理员账号已存在")

        try:
            with DBManager() as cursor:
                cursor.execute(
                    """
                    INSERT INTO sys_user (username, password, nickname, role)
                    VALUES (%s, %s, %s, 'admin')
                    """,
                    (username, generate_password_hash(password), nickname),
                )
        except pymysql.err.IntegrityError as exc:
            raise click.ClickException("管理员账号已存在") from exc

        click.echo(f"管理员 {username} 创建成功。")

    @app.cli.command("reset-admin-password")
    @click.option("--username", prompt="管理员账号")
    @click.password_option(confirmation_prompt=True)
    def reset_admin_password(username: str, password: str) -> None:
        """安全重置管理员密码，并撤销该账号现有的刷新会话。"""
        try:
            username = validate_username(username)
            password = validate_password(password, username)
        except ValidationError as exc:
            raise click.ClickException(exc.message) from exc

        user = query_one(
            "SELECT id FROM sys_user WHERE username = %s AND role = 'admin'",
            (username,),
        )
        if not user:
            raise click.ClickException("管理员账号不存在")

        password_hash = generate_password_hash(password)
        with DBManager(transactional=True) as cursor:
            cursor.execute(
                "UPDATE sys_user SET password = %s WHERE id = %s AND role = 'admin'",
                (password_hash, user["id"]),
            )
            cursor.execute(
                """
                UPDATE sys_auth_refresh_token
                SET revoked_at = UTC_TIMESTAMP(6)
                WHERE account_type = 'admin' AND user_id = %s AND revoked_at IS NULL
                """,
                (user["id"],),
            )

        click.echo(f"管理员 {username} 的密码已重置，现有登录会话已撤销。")
