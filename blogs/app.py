"""Flask 应用工厂与路由装配。

四层结构：界面层（pages）→ 控制层（controllers）→ 数据访问层（dao）
→ 实体/值对象（entities）。本模块只负责装配依赖与注册路由。
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, render_template, url_for

from config import Config
from controllers.comment_controller import CommentController
from controllers.login_controller import LoginController
from controllers.post_controller import PostController
from controllers.reply_controller import ReplyController
from controllers.search_controller import SearchController
from dao.comment_dao import CommentDAO
from dao.member_dao import MemberDAO
from dao.post_dao import PostDAO
from database import init_db
from pages.login_page import LoginPage
from pages.post_detail_page import PostDetailPage
from pages.search_page import SearchPage


def create_app(test_config=None) -> Flask:
    """创建并配置 Flask 应用。"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db_path = str(app.config["DATABASE"])
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    init_db(db_path)

    # 依赖装配：DAO 唯一持有数据库路径，控制器只依赖 DAO。
    post_dao = PostDAO(db_path)
    comment_dao = CommentDAO(db_path)
    member_dao = MemberDAO(db_path)

    login_controller = LoginController(member_dao)
    search_controller = SearchController(post_dao)
    post_controller = PostController(post_dao)
    comment_controller = CommentController(
        comment_dao, app.config.get("COMMENT_PAGE_SIZE", 20)
    )
    reply_controller = ReplyController(
        comment_dao, comment_controller, login_controller
    )

    # 边界类实例（每个页面一个）。
    search_page = SearchPage(search_controller)
    post_detail_page = PostDetailPage(
        post_controller,
        comment_controller,
        reply_controller,
        login_controller,
    )
    login_page = LoginPage(login_controller)

    # 路由表：界面层入口。
    app.add_url_rule(
        "/", endpoint="index", view_func=lambda: redirect(url_for("search"))
    )
    app.add_url_rule(
        "/search",
        endpoint="search",
        view_func=search_page.show,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/post/<int:post_id>",
        endpoint="post_detail",
        view_func=post_detail_page.show,
        methods=["GET"],
    )
    app.add_url_rule(
        "/post/<int:post_id>/reply",
        endpoint="start_reply",
        view_func=post_detail_page.start_reply,
        methods=["GET"],
    )
    app.add_url_rule(
        "/post/<int:post_id>/reply",
        endpoint="submit_reply",
        view_func=post_detail_page.submit_reply,
        methods=["POST"],
    )
    app.add_url_rule(
        "/login", endpoint="login", view_func=login_page.show, methods=["GET"]
    )
    app.add_url_rule(
        "/login",
        endpoint="login_submit",
        view_func=login_page.submit,
        methods=["POST"],
    )
    app.add_url_rule(
        "/logout", endpoint="logout", view_func=login_page.logout, methods=["POST"]
    )

    @app.context_processor
    def inject_auth_context():
        """向全部模板注入登录态，供页头与回复面板使用。"""
        return {
            "current_member_name": login_controller.current_member_name,
            "is_logged_in": login_controller.is_logged_in(),
        }

    @app.errorhandler(404)
    def handle_not_found(error):
        return (
            render_template("error.html", message="页面不存在", code=404),
            404,
        )

    @app.errorhandler(500)
    def handle_server_error(error):
        app.logger.error("服务器内部错误：%s", error)
        return (
            render_template("error.html", message="服务器内部错误", code=500),
            500,
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
