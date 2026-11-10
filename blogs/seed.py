"""演示数据初始化脚本：python seed.py

会删除并重建数据库文件，然后写入会员、帖子与评论演示数据。
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from werkzeug.security import generate_password_hash

from config import Config
from database import connection, init_db, to_db_timestamp

MEMBERS = [
    ("alice", "alice123"),
    ("bob", "bob123"),
    ("carol", "carol123"),
]

POSTS = [
    (
        "alice",
        "欢迎来到博客系统",
        """欢迎来到「博客系统」演示站点。

本系统是《博客系统（浏览帖子）· 软件设计说明书》的参考实现，采用 Python 3 + Flask + SQLite，按界面层、控制层、数据访问层、实体/值对象四层组织。

当前版本覆盖五个用例：
1. 检索帖子（按标题关键词）
2. 阅读帖子详细内容
3. 浏览评论（每页 20 条，倒序）
4. 回复帖子（需登录）
5. 登录（凭证校验与登录态）

你可以从顶部检索框开始，输入标题关键词，例如“Flask”“分页”或“软件工程”。""",
        datetime(2026, 10, 1, 9, 0),
    ),
    (
        "bob",
        "用 Flask 搭建分层博客应用",
        """Flask 的轻量并不意味着可以忽略结构。这个项目把每个用例拆成一个控制器，把 SQL 收进 DAO，界面层只负责取参数和渲染模板。

一次检索请求的协作链如下：
界面层（SearchPage）→ 控制层（SearchController）→ 数据访问层（PostDAO）→ 实体（Post）。

这样做的好处是：控制器不关心 SQL 方言，DAO 不关心 HTTP，实体保持为纯数据对象；测试可以分别针对 DAO、控制器和页面进行。

数据库连接在每次请求内创建，开启外键约束，并通过 schema.sql 统一初始化。""",
        datetime(2026, 10, 3, 10, 30),
    ),
    (
        "alice",
        "SQLite 分页查询实践：LIMIT 与 OFFSET",
        """SQLite 的分页通常写作：

SELECT * FROM comment
WHERE post_id = ?
ORDER BY created_at DESC
LIMIT ? OFFSET ?;

其中 OFFSET = (页码 - 1) × 每页条数。本系统每页固定 20 条，评论按发表时间倒序排列。

边界处理同样重要：
- 评论总数不超过 20 时，不显示翻页控件；
- 第一页禁用“上一页”，最后一页禁用“下一页”；
- 直接访问越界页码时，钳制到最近的有效页，而不是返回空列表。

配合 (post_id, created_at DESC) 复合索引，分页查询在演示数据量下足够轻快。""",
        datetime(2026, 10, 5, 14, 0),
    ),
    (
        "carol",
        "软件工程课程设计复盘",
        """课程设计最容易被低估的部分不是写代码，而是把需求、分析与设计对齐。

这次复盘的三点体会：
1. 用例规格说明书要把扩展流写全，A-2、A-4 这些分支最终都会变成页面上的判断。
2. 分析类图不要混入实现技术词；到了设计类图，再明确 Flask 路由、session 与 SQLite。
3. 顺序图的生命线必须能在设计类图中找到对应类，否则实现时一定缺东西。

把图件当作“可执行的约定”，编码阶段会顺畅很多。""",
        datetime(2026, 10, 8, 16, 20),
    ),
    (
        "bob",
        "如何写好一份用例规格说明书",
        """一份可用的用例规格说明书，至少应包含：用例编号、参与者、触发器、前置/后置条件、基本事件流、扩展事件流、数据需求与业务规则。

写作时注意：
- 基本事件流按“用户动作 / 系统响应”交替描述，避免混入界面细节；
- 扩展流编号与主流程步骤对应，例如 A-2 表示主流程第 2 步的替代路径；
- 业务规则单独列出，便于在设计阶段落到类常量或校验逻辑；
- 待定问题不要藏起来，它们决定了后续假设清单。

本项目的评论每页 20 条、按时间倒序，就是两条明确的业务规则。""",
        datetime(2026, 10, 12, 11, 10),
    ),
    (
        "carol",
        "评论排序为什么选择倒序",
        """评论区默认按发表时间倒序，新回复出现在最上方。这样做有两个直接好处：

第一，用户提交回复后能立即看到自己的内容，反馈闭环更短；
第二，分页第一页始终承载最新讨论，不必翻到最后一页。

实现上，排序键使用 created_at DESC，并以 id DESC 作为同一秒内的稳定次序。新增评论只需 INSERT，无需调整既有数据。

当然，倒序并非唯一选择；如果要做“楼层”式讨论，排序与分页策略都需要重新设计，这已超出当前“浏览帖子”的用例范围。""",
        datetime(2026, 10, 15, 8, 45),
    ),
]

COMMENT_TEMPLATES = [
    "写得很清楚，分层之后代码确实好维护多了。",
    "请问评论分页的页码越界时，页面会怎么处理？",
    "已收藏，准备照着这个结构做课程设计。",
    "SQLite 的 LIMIT/OFFSET 在小数据量下够用，配合索引更稳。",
    "用例规格说明书那一篇很实用，扩展流终于写全了。",
    "同意，倒序展示能让新回复第一时间被看到。",
    "如果后续支持发帖，帖子 DAO 还需要补一个保存方法。",
    "Flask 的 session 用来承载登录态很轻便，但密钥要记得换。",
    "外键级联删除这个点很容易漏，感谢提醒。",
    "建议再补一组分页边界测试，尤其是 20 条和 21 条。",
    "文章结构清晰，读起来不费力。",
    "期待后续增量：发帖、编辑和删除。",
]

# 每个帖子预置的评论数量：45（3 页）、20（恰好一页边界）、3、0、1、0。
COMMENT_COUNTS = [45, 20, 3, 0, 1, 0]


def seed_database(db_path: Optional[str] = None) -> Dict[str, int]:
    """重建数据库并写入演示数据，返回各表记录数。"""
    path = Path(db_path or Config.DATABASE)

    for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
        if candidate.exists():
            candidate.unlink()

    init_db(str(path))

    with connection(str(path)) as conn:
        member_ids: Dict[str, int] = {}
        for username, password in MEMBERS:
            cursor = conn.execute(
                "INSERT INTO member (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            member_ids[username] = int(cursor.lastrowid)

        post_ids = []
        for author, title, content, created_at in POSTS:
            cursor = conn.execute(
                """
                INSERT INTO post (title, content, created_at, author_id)
                VALUES (?, ?, ?, ?)
                """,
                (
                    title,
                    content,
                    to_db_timestamp(created_at),
                    member_ids[author],
                ),
            )
            post_ids.append(int(cursor.lastrowid))

        comment_rows = []
        author_names = [username for username, _ in MEMBERS]
        base_date = datetime(2026, 10, 20, 9, 0)
        for index, post_id in enumerate(post_ids):
            count = COMMENT_COUNTS[index]
            for offset in range(count):
                author = author_names[offset % len(author_names)]
                created_at = base_date + timedelta(days=index, minutes=offset)
                comment_rows.append(
                    (
                        COMMENT_TEMPLATES[offset % len(COMMENT_TEMPLATES)],
                        to_db_timestamp(created_at),
                        post_id,
                        member_ids[author],
                    )
                )

        conn.executemany(
            """
            INSERT INTO comment (content, created_at, post_id, author_id)
            VALUES (?, ?, ?, ?)
            """,
            comment_rows,
        )

    return {
        "member": len(MEMBERS),
        "post": len(POSTS),
        "comment": len(comment_rows),
    }


def main() -> int:
    summary = seed_database()
    print("演示数据初始化完成：")
    print(f"  会员 {summary['member']} 条")
    print(f"  帖子 {summary['post']} 条")
    print(f"  评论 {summary['comment']} 条")
    print(f"  数据库：{Path(Config.DATABASE).resolve()}")
    print("演示账号：alice / alice123、bob / bob123、carol / carol123")
    return 0


if __name__ == "__main__":
    sys.exit(main())
