"""检索页面（UC1 边界类）。"""

from __future__ import annotations

from flask import render_template, request

from controllers.search_controller import SearchController


class SearchPage:
    """检索界面：接收关键词并展示匹配帖子列表。"""

    def __init__(self, search_controller: SearchController) -> None:
        self._search_controller = search_controller

    def show(self):
        """展示检索界面或检索结果（支持 GET/POST 携带 keyword）。"""
        keyword = (request.values.get("keyword") or "").strip()
        searched = bool(keyword)
        posts = self._search_controller.search_posts(keyword) if searched else []
        return render_template(
            "search.html",
            keyword=keyword,
            posts=posts,
            searched=searched,
        )
