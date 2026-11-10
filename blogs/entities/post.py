"""帖子实体。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Post:
    """帖子正文单元（对应数据库表 post）。"""

    id: int
    title: str
    content: str
    created_at: datetime
    author_id: int
    author_name: str = ""
