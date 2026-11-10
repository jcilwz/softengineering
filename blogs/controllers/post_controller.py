"""帖子控制器（UC2）。"""

from __future__ import annotations

from typing import Optional

from dao.post_dao import PostDAO
from entities.post import Post


class PostController:
    """编排帖子详情读取流程。"""

    def __init__(self, post_dao: PostDAO) -> None:
        self._post_dao = post_dao

    def get_post_detail(self, post_id: int) -> Optional[Post]:
        """查看帖子详情；帖子不存在或已删除时返回 None（扩展流 A-2）。"""
        return self._post_dao.find_by_id(post_id)
