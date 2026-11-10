"""评论实体（回复即评论，假设 1）。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Comment:
    """附属于帖子的评论。"""

    id: Optional[int]
    content: str
    created_at: datetime
    post_id: int
    author_id: int
    author_name: str = ""

    @classmethod
    def new(
        cls,
        content: str,
        post_id: int,
        author_id: int,
        created_at: Optional[datetime] = None,
    ) -> "Comment":
        """构造尚未持久化的新评论（id 为空）。"""
        return cls(
            id=None,
            content=content,
            created_at=created_at or datetime.now(),
            post_id=post_id,
            author_id=author_id,
        )
