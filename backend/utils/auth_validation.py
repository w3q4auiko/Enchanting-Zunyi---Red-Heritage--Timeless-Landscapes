"""账号输入校验与密码策略。"""

import re
import unicodedata

USERNAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{3,31}$")
COMMON_PASSWORDS = {
    "12345678",
    "password",
    "password123",
    "qwerty123",
    "admin123",
    "11111111",
}


class ValidationError(ValueError):
    """可安全返回给客户端的字段校验错误。"""

    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


def validate_username(value) -> str:
    """规范化账号并限制为可预测、可索引的 ASCII 标识符。"""
    username = str(value or "").strip().lower()
    if not USERNAME_PATTERN.fullmatch(username):
        raise ValidationError(
            "username",
            "账号须为 4–32 位，以字母开头，仅可包含字母、数字、点、下划线或连字符",
        )
    return username


def normalize_login_username(value) -> str:
    """兼容历史账号登录；严格账号规则只约束新注册数据。"""
    username = str(value or "").strip()
    if not 1 <= len(username) <= 64:
        raise ValidationError("username", "请输入有效账号")
    if any(unicodedata.category(char).startswith("C") for char in username):
        raise ValidationError("username", "账号包含不可使用的控制字符")
    return username


def validate_nickname(value) -> str:
    """校验公开昵称，拒绝控制字符和异常长度。"""
    nickname = str(value or "").strip()
    if not 2 <= len(nickname) <= 30:
        raise ValidationError("nickname", "昵称长度须为 2–30 个字符")
    if any(unicodedata.category(char).startswith("C") for char in nickname):
        raise ValidationError("nickname", "昵称包含不可使用的控制字符")
    return nickname


def validate_password(value, username: str = "") -> str:
    """执行服务端密码策略；客户端校验仅用于改善交互。"""
    password = str(value or "")
    if not 8 <= len(password) <= 128:
        raise ValidationError("password", "密码长度须为 8–128 位")
    if password.lower() in COMMON_PASSWORDS:
        raise ValidationError("password", "该密码过于常见，请更换更安全的密码")
    if username and username.lower() in password.lower():
        raise ValidationError("password", "密码不能包含完整账号")

    character_groups = sum(
        bool(pattern.search(password))
        for pattern in (re.compile(r"[a-z]"), re.compile(r"[A-Z]"), re.compile(r"\d"), re.compile(r"[^A-Za-z0-9]"))
    )
    if character_groups < 3:
        raise ValidationError("password", "密码须包含大小写字母、数字、特殊字符中的至少三类")
    return password


def validate_login_payload(data: dict) -> tuple[str, str, bool]:
    """校验登录请求并返回账号、密码和记住登录选项。"""
    username = normalize_login_username(data.get("username"))
    password = str(data.get("password") or "")
    if not password or len(password) > 128:
        raise ValidationError("password", "请输入有效密码")
    return username, password, data.get("remember") is True
