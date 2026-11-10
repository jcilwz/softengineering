"""DAO 层与值对象单元测试。"""

from __future__ import annotations

from pathlib import Path

from dao.comment_dao import CommentDAO
from dao.member_dao import MemberDAO
from dao.post_dao import PostDAO
from database import connection
from entities.comment import Comment
from entities.page_result import PageResult


def test_find_by_title_matches_title_only(db_path: Path):
    dao = PostDAO(str(db_path))

    results = dao.find_by_title("Flask")
    assert [post.title for post in results] == ["用 Flask 搭建分层博客应用"]
    assert results[0].author_name == "bob"

    # “协作链”只出现在正文中，不应命中（业务规则 B-1）。
    assert dao.find_by_title("协作链") == []
    assert dao.find_by_title("") == []
    assert dao.find_by_title("   ") == []
    # LIKE 通配符按字面量处理，避免“%”命中全部帖子。
    assert dao.find_by_title("%") == []
    assert dao.find_by_title("_") == []


def test_find_by_id_existing_and_missing(db_path: Path):
    dao = PostDAO(str(db_path))

    post = dao.find_by_id(1)
    assert post is not None
    assert post.title == "欢迎来到博客系统"
    assert post.author_name == "alice"
    assert dao.find_by_id(9999) is None


def test_comment_count_boundaries(db_path: Path):
    dao = CommentDAO(str(db_path))

    assert dao.count_by_post(1) == 45
    assert dao.count_by_post(2) == 20
    assert dao.count_by_post(3) == 3
    assert dao.count_by_post(4) == 0


def test_comment_pagination_offset_and_order(db_path: Path):
    dao = CommentDAO(str(db_path))

    first = dao.find_page(1, 1, 20)
    assert first.page == 1
    assert first.total == 45
    assert first.total_pages == 3
    assert len(first.items) == 20
    assert first.has_prev is False
    assert first.has_next is True

    second = dao.find_page(1, 2, 20)
    assert len(second.items) == 20

    third = dao.find_page(1, 3, 20)
    assert len(third.items) == 5
    assert third.has_prev is True
    assert third.has_next is False

    # 倒序：第一页首条最新，第三页末条最旧。
    assert first.items[0].created_at > second.items[0].created_at
    assert second.items[0].created_at > third.items[0].created_at
    assert first.items[0].id == 45
    assert third.items[-1].id == 1

    # 越过后仍返回空条目，真实页码由控制层钳制。
    beyond = dao.find_page(1, 4, 20)
    assert beyond.items == []
    assert beyond.total == 45


def test_comment_save_inserts_newest_first(db_path: Path):
    dao = CommentDAO(str(db_path))
    new_id = dao.save(Comment.new("DAO 层新增评论", post_id=1, author_id=1))

    assert new_id > 0
    assert dao.count_by_post(1) == 46

    page = dao.find_page(1, 1, 20)
    assert page.items[0].id == new_id
    assert page.items[0].content == "DAO 层新增评论"
    assert page.items[0].author_name == "alice"


def test_comment_cascade_delete(db_path: Path):
    dao = CommentDAO(str(db_path))
    assert dao.count_by_post(1) == 45

    with connection(str(db_path)) as conn:
        conn.execute("DELETE FROM post WHERE id = ?", (1,))

    assert dao.count_by_post(1) == 0


def test_member_lookup_and_password_verification(db_path: Path):
    dao = MemberDAO(str(db_path))

    member = dao.find_by_username("alice")
    assert member is not None
    assert member.verify_password("alice123") is True
    assert member.verify_password("wrong-password") is False

    assert dao.find_by_username("nobody") is None
    assert dao.find_by_username("") is None


def test_page_result_value_object():
    result = PageResult(page=1, page_size=20, total=45, items=[])
    assert result.total_pages == 3
    assert result.has_prev is False
    assert result.has_next is True

    empty = PageResult(page=1, page_size=20, total=0, items=[])
    assert empty.total_pages == 1
    assert empty.has_prev is False
    assert empty.has_next is False

    last = PageResult(page=3, page_size=20, total=41, items=[])
    assert last.total_pages == 3
    assert last.has_next is False
