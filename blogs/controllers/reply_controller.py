"""回复控制器（UC4）。"""

from __future__ import annotations

from dao.comment_dao import CommentDAO
from controllers.comment_controller import CommentController
from controllers.login_controller import LoginController
from entities.comment import Comment
from entities.page_result import PageResult


class ReplyController:
    """编排登录判定、回复保存与评论刷新。"""

    def __init__(
        self,
        comment_dao: CommentDAO,
        comment_controller: CommentController,
        login_controller: LoginController,
    ) -> None:
        self._comment_dao = comment_dao
        self._comment_controller = comment_controller
        self._login_controller = login_controller

    def is_logged_in(self) -> bool:
        """委托登录控制器判定登录状态（扩展流 A-2 分支依据）。"""
        return self._login_controller.is_logged_in()

    def submit_reply(self, post_id: int, member_id: int, content: str) -> bool:
        """提交回复。

        前置条件：已登录、内容非空。
        空内容返回 False（扩展流 A-4）；保存成功返回 True。
        """
        content = (content or "").strip()
        if not content:
            return False

        comment = Comment.new(content=content, post_id=post_id, author_id=member_id)
        self._comment_dao.save(comment)
        return True

    def refresh_comments(self, post_id: int) -> PageResult:
        """保存成功后刷新评论列表（第 1 页，新回复居首）。"""
        return self._comment_controller.browse_comments(post_id, 1)
