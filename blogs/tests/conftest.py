"""pytest 公共夹具：每个测试使用独立的临时数据库。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest  # noqa: E402

from app import create_app  # noqa: E402
from seed import seed_database  # noqa: E402


@pytest.fixture()
def app(tmp_path: Path):
    db_path = tmp_path / "blog-test.sqlite3"
    seed_database(str(db_path))
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": str(db_path),
            "SECRET_KEY": "test-secret",
            "COMMENT_PAGE_SIZE": 20,
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_path(app) -> Path:
    return Path(app.config["DATABASE"])


@pytest.fixture()
def login(client):
    """登录辅助函数：默认以 alice 登录。"""

    def _login(username: str = "alice", password: str = "alice123", next_url=None):
        data = {"username": username, "password": password}
        if next_url is not None:
            data["next"] = next_url
        return client.post("/login", data=data)

    return _login
