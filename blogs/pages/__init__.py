"""界面层（Flask 路由处理 + Jinja2 模板）。"""

from pages.login_page import LoginPage
from pages.post_detail_page import PostDetailPage
from pages.search_page import SearchPage

__all__ = ["SearchPage", "PostDetailPage", "LoginPage"]
