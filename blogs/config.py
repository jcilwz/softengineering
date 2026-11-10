"""应用配置。

配置集中于 Flask 配置项：数据库路径、会话密钥、评论每页条数。
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """博客系统默认配置。"""

    # 生产环境请通过环境变量 BLOG_SECRET_KEY 覆盖。
    SECRET_KEY = os.environ.get("BLOG_SECRET_KEY", "dev-secret-key-change-me")

    # 数据库文件默认放在 instance/ 下，避免提交到版本库。
    DATABASE = os.environ.get(
        "BLOG_DATABASE", str(BASE_DIR / "instance" / "blog.sqlite3")
    )

    # 评论分页：业务规则 B-1，每页固定 20 条。
    COMMENT_PAGE_SIZE = 20

    # 会话 Cookie 安全设置（本地演示默认关闭 secure，HTTPS 部署时开启）。
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
