"""分页结果值对象。"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from entities.comment import Comment


@dataclass(frozen=True)
class PageResult:
    """封装页码、总页数、每页条数与当前页条目。"""

    page: int
    page_size: int
    total: int
    items: List[Comment]

    def __post_init__(self) -> None:
        if self.page_size <= 0:
            raise ValueError("每页条数必须大于 0")
        if self.page < 1:
            raise ValueError("页码必须大于等于 1")

    @property
    def total_pages(self) -> int:
        """总页数；无数据时记为 1 页，便于页面展示。"""
        if self.total <= 0:
            return 1
        return math.ceil(self.total / self.page_size)

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
