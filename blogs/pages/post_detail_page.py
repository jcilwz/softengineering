"""详情页面（UC2 / UC3 / UC4 边界类）。"""

from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from controllers.comment_controller import CommentController
from controllers.login_controller import LoginController
from controllers.post_controller import PostController
from controllers.reply_controller import ReplyController

POST_NOT_FOUND_MESSAGE = "帖子不存在或已删除"


class PostDetailPage:
    """帖子详情界面：展示正文与分页评论，承载回复扩展点。"""

    def __init__(
        self,
        post_controller: PostController,
        comment_controller: CommentController,
        reply_controller: ReplyController,
        login_controller: LoginController,
    ) -> None:
        self._post_controller = post_controller
        self._comment_controller = comment_controller
        self._reply_controller = reply_controller
        self._login_controller = login_controller

    def show(self, post_id: int):
        """展示帖子详情与第 page 页评论；帖子不存在时提示（A-2）。"""
        post = self._post_controller.get_post_detail(post_id)
        if post is None:
            return self._render_not_found()

        page = request.args.get("page", 1, type=int) or 1
        comments = self._comment_controller.browse_comments(post_id, page)
        return render_template(
            "post_detail.html",
            post=post,
            comments=comments,
            error_message=None,
        )

    def start_reply(self, post_id: int):
        """点击“回复”：判定登录状态（UC4 步骤 2）。

        未登录：提示“请先登录”并转登录页，登录后返回原帖（A-2）；
        已登录：返回详情页回复输入区。
        """
        post = self._post_controller.get_post_detail(post_id)
        if post is None:
            return self._render_not_found()

        if not self._reply_controller.is_logged_in():
            flash("请先登录", "warning")
            return redirect(
                url_for("login", next=url_for("post_detail", post_id=post_id))
            )

        return redirect(url_for("post_detail", post_id=post_id, _anchor="reply"))

    def submit_reply(self, post_id: int):
        """提交回复：校验登录态与内容，成功后刷新评论列表。"""
        post = self._post_controller.get_post_detail(post_id)
        if post is None:
            return self._render_not_found()

        if not self._reply_controller.is_logged_in():
            flash("请先登录", "warning")
            return redirect(
                url_for("login", next=url_for("post_detail", post_id=post_id))
            )

        member_id = self._login_controller.current_member_id
        if member_id is None:  # 登录态在请求间失效的兜底
            flash("请先登录", "warning")
            return redirect(
                url_for("login", next=url_for("post_detail", post_id=post_id))
            )

        content = request.form.get("content", "")
        if not self._reply_controller.submit_reply(post_id, member_id, content):
            flash("回复不能为空", "error")
            return redirect(
                url_for("post_detail", post_id=post_id, _anchor="reply")
            )

        flash("回复成功", "success")
        return redirect(url_for("post_detail", post_id=post_id))

    @staticmethod
    def _render_not_found():
        return (
            render_template(
                "post_detail.html",
                post=None,
                comments=None,
                error_message=POST_NOT_FOUND_MESSAGE,
            ),
            404,
        )
