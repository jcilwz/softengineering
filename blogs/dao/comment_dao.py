"""评论数据访问对象（含分页值对象创建）。"""

from __future__ import annotations

import sqlite3
from typing import List

from database import connection, parse_datetime, to_db_timestamp
from entities.comment import Comment
from entities.page_result import PageResult


class CommentDAO:
    """封装 comment 表的计数、分页查询与新增。"""

    _SELECT = """
        SELECT c.id, c.content, c.created_at, c.post_id, c.author_id,
               m.username AS author_name
        FROM comment AS c
        JOIN member AS m ON m.id = c.author_id
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def count_by_post(self, post_id: int) -> int:
        """统计某帖子的评论总数。"""
        with connection(self._db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM comment WHERE post_id = ?",
                (post_id,),
            ).fetchone()
        return int(row["total"]) if row is not None else 0

    def find_page(self, post_id: int, page: int, page_size: int) -> PageResult:
        """分页查询评论，按发表时间倒序（假设 2）。

        页码由控制层保证 >= 1；本方法仍做防御性归一化。
        返回以当前页条目组装的分页结果值对象。
        """
        page = max(1, int(page))
        page_size = max(1, int(page_size))
        offset = (page - 1) * page_size

        with connection(self._db_path) as conn:
            total_row = conn.execute(
                "SELECT COUNT(*) AS total FROM comment WHERE post_id = ?",
                (post_id,),
            ).fetchone()
            total = int(total_row["total"]) if total_row is not None else 0

            sql = self._SELECT + """
                WHERE c.post_id = ?
                ORDER BY c.created_at DESC, c.id DESC
                LIMIT ? OFFSET ?
            """
            rows = conn.execute(sql, (post_id, page_size, offset)).fetchall()

        items: List[Comment] = [self._to_comment(row) for row in rows]
        return PageResult(page=page, page_size=page_size, total=total, items=items)

    def save(self, comment: Comment) -> int:
        """保存新评论，返回自增主键。"""
        sql = """
            INSERT INTO comment (content, created_at, post_id, author_id)
            VALUES (?, ?, ?, ?)
        """
        with connection(self._db_path) as conn:
            cursor = conn.execute(
                sql,
                (
                    comment.content,
                    to_db_timestamp(comment.created_at),
                    comment.post_id,
                    comment.author_id,
                ),
            )
            return int(cursor.lastrowid)

    @staticmethod
    def _to_comment(row: sqlite3.Row) -> Comment:
        return Comment(
            id=int(row["id"]),
            content=str(row["content"]),
            created_at=parse_datetime(row["created_at"]),
            post_id=int(row["post_id"]),
            author_id=int(row["author_id"]),
            author_name=str(row["author_name"]),
        )
