"""检索控制器（UC1）。"""

from __future__ import annotations

from typing import List

from dao.post_dao import PostDAO
from entities.post import Post


class SearchController:
    """编排按标题关键词检索帖子的流程。"""

    def __init__(self, post_dao: PostDAO) -> None:
        self._post_dao = post_dao

    def search_posts(self, keyword: str) -> List[Post]:
        """检索帖子。

        前置条件：关键词非空；空关键词返回空列表。
        后置条件：返回匹配帖子列表（可为空列表，对应扩展流 A-3）。
        """
        keyword = (keyword or "").strip()
        if not keyword:
            return []
        return self._post_dao.find_by_title(keyword)
