"""评论控制器（UC3）。"""

from __future__ import annotations

import math
from typing import Optional

from dao.comment_dao import CommentDAO
from entities.page_result import PageResult


class CommentController:
    """编排评论分页浏览流程。"""

    # 业务规则 B-1：每页固定 20 条评论。
    PAGE_SIZE = 20

    def __init__(
        self, comment_dao: CommentDAO, page_size: Optional[int] = None
    ) -> None:
        self._comment_dao = comment_dao
        self._page_size = page_size if page_size and page_size > 0 else self.PAGE_SIZE

    @property
    def page_size(self) -> int:
        return self._page_size

    def calculate_total_pages(self, total: int) -> int:
        """按评论总数计算总页数；无评论时按 1 页处理。"""
        if total <= 0:
            return 1
        return math.ceil(total / self._page_size)

    def browse_comments(self, post_id: int, page: int = 1) -> PageResult:
        """浏览指定页评论。

        页码越界时钳制到有效范围（扩展流 A-2/A-3：对应按钮不可用，
        直接访问越界页码时回到最近的有效页）。
        """
        total = self._comment_dao.count_by_post(post_id)
        total_pages = self.calculate_total_pages(total)
        safe_page = min(max(int(page or 1), 1), total_pages)
        return self._comment_dao.find_page(post_id, safe_page, self._page_size)
