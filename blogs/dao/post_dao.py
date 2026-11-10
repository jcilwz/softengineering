"""帖子数据访问对象。"""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from database import connection, parse_datetime
from entities.post import Post


class PostDAO:
    """封装 post 表的查询。"""

    _SELECT = """
        SELECT p.id, p.title, p.content, p.created_at, p.author_id,
               m.username AS author_name
        FROM post AS p
        JOIN member AS m ON m.id = p.author_id
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def find_by_title(self, keyword: str) -> List[Post]:
        """按标题模糊匹配帖子（业务规则 B-1：仅标题，不含正文/作者）。

        关键词为空时返回空列表；结果按发表时间倒序。
        """
        keyword = (keyword or "").strip()
        if not keyword:
            return []

        sql = self._SELECT + """
            WHERE p.title LIKE ? ESCAPE '\\'
            ORDER BY p.created_at DESC, p.id DESC
        """
        pattern = f"%{self._escape_like(keyword)}%"
        with connection(self._db_path) as conn:
            rows = conn.execute(sql, (pattern,)).fetchall()
        return [self._to_post(row) for row in rows]

    def find_by_id(self, post_id: int) -> Optional[Post]:
        """按主键查询帖子；不存在返回 None（扩展流 A-2 判定依据）。"""
        sql = self._SELECT + " WHERE p.id = ?"
        with connection(self._db_path) as conn:
            row = conn.execute(sql, (post_id,)).fetchone()
        return self._to_post(row) if row is not None else None

    @staticmethod
    def _escape_like(value: str) -> str:
        """转义 LIKE 通配符，使用户输入按字面量匹配。"""
        return (
            value.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )

    @staticmethod
    def _to_post(row: sqlite3.Row) -> Post:
        return Post(
            id=int(row["id"]),
            title=str(row["title"]),
            content=str(row["content"]),
            created_at=parse_datetime(row["created_at"]),
            author_id=int(row["author_id"]),
            author_name=str(row["author_name"]),
        )
