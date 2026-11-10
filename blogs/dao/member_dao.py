"""会员数据访问对象。"""

from __future__ import annotations

import sqlite3
from typing import Optional

from database import connection
from entities.member import Member


class MemberDAO:
    """封装 member 表的查询。"""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def find_by_username(self, username: str) -> Optional[Member]:
        """按用户名精确查询；无记录返回 None（凭证错误判定依据）。"""
        username = (username or "").strip()
        if not username:
            return None

        with connection(self._db_path) as conn:
            row = conn.execute(
                "SELECT id, username, password FROM member WHERE username = ?",
                (username,),
            ).fetchone()
        return self._to_member(row) if row is not None else None

    def find_by_id(self, member_id: int) -> Optional[Member]:
        """按主键查询会员（供扩展使用）。"""
        with connection(self._db_path) as conn:
            row = conn.execute(
                "SELECT id, username, password FROM member WHERE id = ?",
                (member_id,),
            ).fetchone()
        return self._to_member(row) if row is not None else None

    @staticmethod
    def _to_member(row: sqlite3.Row) -> Member:
        return Member(
            id=int(row["id"]),
            username=str(row["username"]),
            password_hash=str(row["password"]),
        )
