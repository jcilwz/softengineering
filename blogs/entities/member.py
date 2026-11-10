"""会员实体。"""

from __future__ import annotations

from dataclasses import dataclass

from werkzeug.security import check_password_hash


@dataclass(frozen=True)
class Member:
    """注册用户账号（对应数据库表 member）。"""

    id: int
    username: str
    password_hash: str

    def verify_password(self, password: str) -> bool:
        """校验明文密码是否与存储的哈希匹配。"""
        return check_password_hash(self.password_hash, password)
