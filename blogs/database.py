"""SQLite 连接与初始化工具。

数据访问层（DAO）通过 ``connection`` 上下文管理器获取连接；
连接统一开启外键约束，保证 comment 的级联删除语义生效。
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Union

BASE_DIR = Path(__file__).resolve().parent
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_connection(db_path: str) -> sqlite3.Connection:
    """创建连接并设置行工厂与外键约束。"""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def connection(db_path: str) -> Iterator[sqlite3.Connection]:
    """事务化连接：正常结束提交，异常回滚，最终关闭。"""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str) -> None:
    """执行 schema.sql，创建全部表与索引（幂等）。"""
    schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    conn = get_connection(db_path)
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def to_db_timestamp(value: datetime) -> str:
    """将 datetime 转为数据库存储格式（精确到秒）。"""
    return value.strftime(TIMESTAMP_FORMAT)


def parse_datetime(value: Union[str, datetime]) -> datetime:
    """将 SQLite 返回的时间值解析为 datetime。"""
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))
