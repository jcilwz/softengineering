"""页面路由与模板渲染测试（主流程 + 扩展流）。"""

from __future__ import annotations

from pathlib import Path

from dao.comment_dao import CommentDAO
from entities.comment import Comment


def test_root_redirects_to_search(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/search"


def test_search_page_initial_state(client):
    response = client.get("/search")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "检索帖子" in html
    assert "输入标题关键词开始检索" in html
    assert "未找到相关帖子" not in html


def test_search_by_title_keyword(client):
    response = client.get("/search?keyword=Flask")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "用 Flask 搭建分层博客应用" in html
    assert "作者 bob" in html
    assert "共找到 <strong>1</strong> 篇帖子" in html
    assert "未找到相关帖子" not in html


def test_search_post_method_and_no_match(client):
    response = client.post("/search", data={"keyword": "SQLite"})
    html = response.get_data(as_text=True)
    assert "SQLite 分页查询实践：LIMIT 与 OFFSET" in html

    response = client.get("/search?keyword=不存在的关键词xyz")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "未找到相关帖子" in html
    assert "共找到 <strong>0</strong> 篇帖子" in html


def test_post_detail_first_page(client):
    response = client.get("/post/1")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "欢迎来到博客系统" in html
    assert "作者 alice" in html
    assert "45 条" in html
    assert "第 1 / 3 页" in html
    assert 'href="/post/1?page=2"' in html
    assert '<span class="page-link is-disabled" aria-disabled="true">上一页</span>' in html


def test_post_detail_last_page_disables_next(client):
    response = client.get("/post/1?page=3")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "第 3 / 3 页" in html
    assert 'href="/post/1?page=2"' in html
    assert '<span class="page-link is-disabled" aria-disabled="true">下一页</span>' in html


def test_post_detail_page_overflow_is_clamped(client):
    response = client.get("/post/1?page=99")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "第 3 / 3 页" in html


def test_exactly_twenty_comments_hides_pagination(client):
    response = client.get("/post/2")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "20 条" in html
    assert "上一页" not in html
    assert "下一页" not in html

    # 越界页码被钳制到第 1 页，仍不出现翻页控件。
    clamped = client.get("/post/2?page=2")
    clamped_html = clamped.get_data(as_text=True)
    assert clamped.status_code == 200
    assert "20 条" in clamped_html
    assert "上一页" not in clamped_html


def test_post_without_comments(client):
    response = client.get("/post/4")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "0 条" in html
    assert "暂无评论，来发表第一条回复吧。" in html


def test_post_not_found(client):
    response = client.get("/post/9999")
    html = response.get_data(as_text=True)

    assert response.status_code == 404
    assert "帖子不存在或已删除" in html
    assert "返回检索" in html


def test_unknown_route_uses_error_page(client):
    response = client.get("/no-such-page")
    html = response.get_data(as_text=True)

    assert response.status_code == 404
    assert "页面不存在" in html


def test_login_failure_shows_message(client):
    response = client.post(
        "/login", data={"username": "alice", "password": "wrong-password"}
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "用户名或密码错误" in html
    assert 'value="alice"' in html

    with client.session_transaction() as session:
        assert "member_id" not in session


def test_login_success_returns_to_next_page(client, login):
    response = login(next_url="/post/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/post/1"

    with client.session_transaction() as session:
        assert session["member_name"] == "alice"
        assert session["member_id"] == 1


def test_login_success_defaults_to_search(client, login):
    response = login()
    assert response.status_code == 302
    assert response.headers["Location"] == "/search"


def test_login_retry_after_wrong_password(client):
    first = client.post(
        "/login", data={"username": "alice", "password": "wrong-password"}
    )
    assert "用户名或密码错误" in first.get_data(as_text=True)

    second = client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
        follow_redirects=True,
    )
    assert "你好，alice" in second.get_data(as_text=True)


def test_login_rejects_open_redirect(client):
    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "alice123",
            "next": "//evil.example/phish",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/search"

    client.post("/logout")
    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "alice123",
            "next": "https://evil.example/phish",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/search"


def test_logout_clears_session(client, login):
    login()
    response = client.post("/logout", follow_redirects=True)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "已退出登录" in html
    assert "你好，alice" not in html

    with client.session_transaction() as session:
        assert "member_id" not in session
        assert "member_name" not in session


def test_guest_reply_is_redirected_to_login(client, db_path: Path):
    response = client.get("/post/1/reply")
    assert response.status_code == 302
    assert response.headers["Location"] == "/login?next=/post/1"

    followed = client.get("/post/1/reply", follow_redirects=True)
    html = followed.get_data(as_text=True)
    assert "请先登录" in html
    assert "回复（需登录）" not in html  # 已离开详情页，进入登录页
    assert CommentDAO(str(db_path)).count_by_post(1) == 45


def test_guest_post_reply_does_not_save(client, db_path: Path):
    response = client.post("/post/1/reply", data={"content": "游客的回复"})

    assert response.status_code == 302
    assert response.headers["Location"] == "/login?next=/post/1"
    assert CommentDAO(str(db_path)).count_by_post(1) == 45


def test_guest_reply_login_then_continue_scenario(client, db_path: Path):
    """场景：游客回复被引导登录，成功后返回原帖并完成回复。"""
    gate = client.get("/post/1/reply")
    assert gate.status_code == 302
    assert gate.headers["Location"] == "/login?next=/post/1"

    login_response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "alice123",
            "next": "/post/1",
        },
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"] == "/post/1"

    reply = client.post(
        "/post/1/reply",
        data={"content": "登录后继续回复"},
        follow_redirects=True,
    )
    html = reply.get_data(as_text=True)
    assert reply.status_code == 200
    assert "登录后继续回复" in html
    assert "46 条" in html
    assert CommentDAO(str(db_path)).count_by_post(1) == 46


def test_logged_in_post_page_shows_reply_form(client, login):
    login()
    response = client.get("/post/1")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert '<textarea id="content" name="content"' in html
    assert "发表回复" in html
    assert "登录后即可回复" not in html


def test_empty_reply_is_rejected(client, login, db_path: Path):
    login()
    response = client.post(
        "/post/1/reply", data={"content": "   "}, follow_redirects=True
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "回复不能为空" in html
    assert CommentDAO(str(db_path)).count_by_post(1) == 45


def test_reply_success_appears_first(client, login, db_path: Path):
    login()
    content = "这是自动化测试新增的回复"
    response = client.post(
        "/post/1/reply", data={"content": content}, follow_redirects=True
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "回复成功" in html
    assert "46 条" in html
    assert content in html
    assert CommentDAO(str(db_path)).count_by_post(1) == 46

    # 新回复位于评论区首位（早于原有的最新评论）。
    assert html.index(content) < html.index("外键级联删除这个点很容易漏")


def test_user_content_is_escaped(client, db_path: Path):
    CommentDAO(str(db_path)).save(
        Comment.new("<script>alert('xss')</script>", post_id=1, author_id=1)
    )

    response = client.get("/post/1")
    html = response.get_data(as_text=True)

    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
