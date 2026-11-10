"""控制器单元测试。"""

from __future__ import annotations

from pathlib import Path

from controllers.comment_controller import CommentController
from controllers.login_controller import LoginController
from controllers.post_controller import PostController
from controllers.reply_controller import ReplyController
from controllers.search_controller import SearchController
from dao.comment_dao import CommentDAO
from dao.member_dao import MemberDAO
from dao.post_dao import PostDAO


def test_search_controller_returns_matches(db_path: Path):
    controller = SearchController(PostDAO(str(db_path)))

    results = controller.search_posts("软件工程")
    assert len(results) == 1
    assert results[0].title == "软件工程课程设计复盘"

    assert controller.search_posts("") == []
    assert controller.search_posts("不存在的关键词") == []


def test_post_controller_missing_post(db_path: Path):
    controller = PostController(PostDAO(str(db_path)))

    assert controller.get_post_detail(1) is not None
    assert controller.get_post_detail(9999) is None


def test_comment_controller_clamps_page(db_path: Path):
    controller = CommentController(CommentDAO(str(db_path)))

    first = controller.browse_comments(1, 0)
    assert first.page == 1
    assert first.total == 45
    assert first.total_pages == 3

    last = controller.browse_comments(1, 99)
    assert last.page == 3
    assert len(last.items) == 5

    assert controller.calculate_total_pages(0) == 1
    assert controller.calculate_total_pages(1) == 1
    assert controller.calculate_total_pages(20) == 1
    assert controller.calculate_total_pages(21) == 2
    assert controller.calculate_total_pages(45) == 3


def test_comment_controller_custom_page_size(db_path: Path):
    controller = CommentController(CommentDAO(str(db_path)), page_size=10)
    result = controller.browse_comments(1, 2)

    assert result.page_size == 10
    assert result.total_pages == 5
    assert len(result.items) == 10


def test_login_controller_establishes_and_clears_session(app, db_path: Path):
    controller = LoginController(MemberDAO(str(db_path)))

    with app.test_request_context():
        assert controller.is_logged_in() is False
        assert controller.verify_credentials("alice", "wrong") is False
        assert controller.is_logged_in() is False

        assert controller.verify_credentials("alice", "alice123") is True
        assert controller.is_logged_in() is True
        assert controller.current_member_id == 1
        assert controller.current_member_name == "alice"

        controller.logout()
        assert controller.is_logged_in() is False
        assert controller.current_member_id is None
        assert controller.current_member_name is None


def test_reply_controller_validates_and_saves(app, db_path: Path):
    comment_dao = CommentDAO(str(db_path))
    comment_controller = CommentController(comment_dao)
    login_controller = LoginController(MemberDAO(str(db_path)))
    controller = ReplyController(comment_dao, comment_controller, login_controller)

    assert controller.submit_reply(1, 1, "   ") is False
    assert comment_dao.count_by_post(1) == 45

    assert controller.submit_reply(1, 1, "  控制器层新增回复  ") is True
    assert comment_dao.count_by_post(1) == 46

    refreshed = controller.refresh_comments(1)
    assert refreshed.page == 1
    assert refreshed.items[0].content == "控制器层新增回复"


def test_reply_controller_login_delegation(app, db_path: Path):
    comment_dao = CommentDAO(str(db_path))
    login_controller = LoginController(MemberDAO(str(db_path)))
    controller = ReplyController(
        comment_dao, CommentController(comment_dao), login_controller
    )

    with app.test_request_context():
        assert controller.is_logged_in() is False
        login_controller.verify_credentials("bob", "bob123")
        assert controller.is_logged_in() is True
