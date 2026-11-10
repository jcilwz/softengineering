# 博客系统（浏览帖子）

《博客系统（浏览帖子）· 软件设计说明书》v1.0 的参考实现，采用 **Python 3 + Flask + SQLite**，按界面层 / 控制层 / 数据访问层 / 实体与值对象四层组织，覆盖 UC1–UC5 五个用例。

## 1. 功能范围

| 用例 | 功能 | 入口 |
|------|------|------|
| UC1 检索帖子 | 按标题关键词检索（仅标题，不分页） | `/search` |
| UC2 阅读帖子详细内容 | 帖子正文 + 评论随详情一并加载 | `/post/<id>` |
| UC3 浏览评论 | 每页 20 条、按发表时间倒序、上一页/下一页 | `/post/<id>?page=N` |
| UC4 回复帖子 | 登录判定、非空校验、保存后刷新评论 | `/post/<id>/reply` |
| UC5 登录 | 用户名 + 密码校验、建立登录态、返回 `next` | `/login` |

角色权限与设计说明书第 8 部分一致：游客可检索、阅读、浏览评论；回复需登录，未登录时提示“请先登录”并在登录后返回原帖。

## 2. 快速开始

```powershell
cd blogs

# 建议使用虚拟环境（可选）
python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt

# 初始化演示数据（会删除并重建 instance/blog.sqlite3）
python seed.py

# 启动开发服务器
python run.py
```

浏览器访问 <http://127.0.0.1:5000>。

### 演示账号

| 用户名 | 密码 |
|--------|------|
| alice | alice123 |
| bob | bob123 |
| carol | carol123 |

演示数据：3 位会员、6 篇帖子、69 条评论。其中第 1 篇 45 条评论（3 页），第 2 篇恰好 20 条（一页边界，不显示翻页控件），第 3 篇 3 条，第 4 篇 0 条，第 5 篇 1 条，第 6 篇 0 条。

> `seed.py` 会**删除重建**数据库文件，仅用于课程演示；不要在有真实数据时执行。

## 3. 目录结构

```text
blogs/
├── app.py                  # 应用工厂、依赖装配、路由注册、错误处理
├── run.py                  # 开发服务器入口
├── config.py               # 数据库路径、密钥、每页条数等配置
├── database.py             # SQLite 连接（外键开启）、事务、schema 初始化
├── schema.sql              # member / post / comment 三表与分页索引
├── seed.py                 # 演示数据初始化
├── requirements.txt
├── requirements-dev.txt
├── entities/               # 实体与值对象
│   ├── post.py             # Post
│   ├── comment.py          # Comment（含 new 工厂）
│   ├── member.py           # Member.verify_password()
│   └── page_result.py      # PageResult（页码/总页数/每页条数/条目）
├── dao/                    # 数据访问层：仅此层出现 SQL
│   ├── post_dao.py
│   ├── comment_dao.py
│   └── member_dao.py
├── controllers/            # 控制层：编排用例、应用业务规则
│   ├── search_controller.py
│   ├── post_controller.py
│   ├── comment_controller.py
│   ├── reply_controller.py
│   └── login_controller.py
├── pages/                  # 界面层：Flask 路由处理类
│   ├── search_page.py
│   ├── post_detail_page.py
│   └── login_page.py
├── templates/              # Jinja2 模板
│   ├── base.html
│   ├── search.html
│   ├── post_detail.html
│   ├── login.html
│   └── error.html
├── static/style.css
├── tests/                  # pytest 测试
└── instance/blog.sqlite3   # 运行时生成，已被 .gitignore 忽略
```

依赖方向严格单向：`pages → controllers → dao → entities`。界面层不写 SQL，DAO 不依赖 Flask，实体不依赖 HTTP。

## 4. 设计类映射（15 类）

| 层 | 中文类名（设计图） | Python 类 | 文件 |
|----|--------------------|-----------|------|
| «boundary» | 检索页面 | `SearchPage` | `pages/search_page.py` |
| «boundary» | 详情页面 | `PostDetailPage` | `pages/post_detail_page.py` |
| «boundary» | 登录页面 | `LoginPage` | `pages/login_page.py` |
| «control» | 检索控制器 | `SearchController` | `controllers/search_controller.py` |
| «control» | 帖子控制器 | `PostController` | `controllers/post_controller.py` |
| «control» | 评论控制器 | `CommentController` | `controllers/comment_controller.py` |
| «control» | 回复控制器 | `ReplyController` | `controllers/reply_controller.py` |
| «control» | 登录控制器 | `LoginController` | `controllers/login_controller.py` |
| «DAO» | 帖子DAO | `PostDAO` | `dao/post_dao.py` |
| «DAO» | 评论DAO | `CommentDAO` | `dao/comment_dao.py` |
| «DAO» | 会员DAO | `MemberDAO` | `dao/member_dao.py` |
| «entity» | 帖子 | `Post` | `entities/post.py` |
| «entity» | 评论 | `Comment` | `entities/comment.py` |
| «entity» | 会员 | `Member` | `entities/member.py` |
| «value object» | 分页结果 | `PageResult` | `entities/page_result.py` |

关键方法（对应设计说明书 7.3）：

| 类 | 方法 |
|----|------|
| `SearchController` | `search_posts(keyword) -> List[Post]` |
| `PostController` | `get_post_detail(post_id) -> Optional[Post]` |
| `CommentController` | `browse_comments(post_id, page) -> PageResult`、`calculate_total_pages(total)` |
| `ReplyController` | `submit_reply(post_id, member_id, content) -> bool`、`refresh_comments(post_id)` |
| `LoginController` | `verify_credentials(username, password) -> bool`、`is_logged_in()`、`current_member_id/name` |
| `PostDAO` | `find_by_title(keyword)`、`find_by_id(post_id)` |
| `CommentDAO` | `find_page(post_id, page, page_size)`、`count_by_post(post_id)`、`save(comment)` |
| `MemberDAO` | `find_by_username(username)` |
| `Member` | `verify_password(password) -> bool` |

## 5. 数据库

```text
member 1 ──── 0..* post      （作者）
member 1 ──── 0..* comment   （作者）
post   1 ──── 0..* comment   （组合：删除帖子级联删除评论）
```

| 表 | 字段 |
|----|------|
| `member` | `id` PK、`username` UNIQUE NOT NULL、`password`（werkzeug 哈希，不存明文） |
| `post` | `id` PK、`title`、`content`、`created_at`、`author_id` → `member(id)` |
| `comment` | `id` PK、`content`、`created_at`、`post_id` → `post(id) ON DELETE CASCADE`、`author_id` → `member(id)` |

- 每个连接执行 `PRAGMA foreign_keys = ON`，保证级联删除生效。
- 评论分页索引：`(post_id, created_at DESC)`。
- 评论排序：`created_at DESC, id DESC`，同一秒内也有稳定次序。

## 6. 路由

| 方法 | 路径 | 端点 | 说明 |
|------|------|------|------|
| GET | `/` | `index` | 重定向到检索页 |
| GET / POST | `/search` | `search` | 检索界面与结果，参数 `keyword` |
| GET | `/post/<int:post_id>` | `post_detail` | 帖子详情，参数 `page` |
| GET | `/post/<int:post_id>/reply` | `start_reply` | “回复”登录判定入口（未登录转 UC5） |
| POST | `/post/<int:post_id>/reply` | `submit_reply` | 提交回复，参数 `content` |
| GET | `/login` | `login` | 登录表单，可选 `next` |
| POST | `/login` | `login_submit` | 凭证校验 |
| POST | `/logout` | `logout` | 退出登录（演示便利功能，不在用例模型内） |

`next` 仅接受站内相对路径（拒绝 `//evil.example`、`https://...`），防止开放重定向。

## 7. 关键实现说明

### UC1 检索
- `SearchController` 去空白后交给 `PostDAO.find_by_title`；SQL 仅匹配 `post.title`（业务规则 B-1），不匹配正文或作者。
- 无匹配时页面显示“未找到相关帖子”（A-3）；关键词为空时不执行查询，显示引导态。
- 检索结果按设计文档“暂不分页”。

### UC2 / UC3 详情与评论
- 帖子不存在时返回 HTTP 404 并提示“帖子不存在或已删除”（A-2）。
- 每页固定 20 条（`CommentController.PAGE_SIZE`），按发表时间倒序（假设 2）。
- `comments.total_pages <= 1` 时完全不渲染翻页控件（A-1）；首页禁用“上一页”，末页禁用“下一页”（A-2/A-3）。
- 直接访问越界页码（如 `?page=99`）会钳制到最近的有效页，避免空白页面；翻页控件本身仍遵循“不可用即不发起查询”。

### UC4 回复
- 游客在详情页看到“回复（需登录）”，点击后进入 `start_reply`：系统判定登录态，提示“请先登录”并跳转登录页，`next` 指回原帖（A-2）。
- 会员提交时再次校验登录态；内容 `strip()` 后为空则提示“回复不能为空”（A-4）。
- 保存成功后重定向到详情第 1 页，新回复因倒序排列显示在评论区首位；`ReplyController.refresh_comments` 提供同一刷新语义。

### UC5 登录
- 密码以 `werkzeug.security.generate_password_hash` 存储，`Member.verify_password` 校验，不存明文（假设 7）。
- 凭证错误时提示“用户名或密码错误”，失败次数不限（假设 6）。
- 登录态由 Flask session 的 `member_id` / `member_name` 承载；session 缺失按未登录处理。

## 8. 配置

| 配置项 / 环境变量 | 默认值 | 说明 |
|-------------------|--------|------|
| `BLOG_DATABASE` | `blogs/instance/blog.sqlite3` | SQLite 文件路径 |
| `BLOG_SECRET_KEY` | 开发默认值 | **生产环境必须覆盖** |
| `COMMENT_PAGE_SIZE` | 20 | 评论每页条数（业务规则 B-1） |

示例：

```powershell
$env:BLOG_SECRET_KEY = "a-long-random-secret"
$env:BLOG_DATABASE = "D:\data\blog.sqlite3"
python run.py
```

## 9. 测试

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

当前共 **39 个测试**，全部通过（Python 3.13 / Flask 3.1.3 / pytest 9.2）：

- `tests/test_dao.py`：标题匹配范围、分页 OFFSET 边界（45/20/0 条、第 3 页 5 条）、倒序、保存、级联删除、会员密码校验、值对象总页数。
- `tests/test_controllers.py`：空关键词、帖子不存在、页码钳制、自定义每页条数、登录态建立/清除、空回复校验、回复刷新。
- `tests/test_pages.py`：三个页面的 GET/POST、404、搜索无结果、翻页控件显隐与禁用、登录失败/成功/`next` 返回、开放重定向拦截、游客回复引导、空回复提示、新回复居首、退出登录、用户内容转义；含“游客回复 → 登录 → 返回原帖继续回复”与“凭证错误后重试”两个场景。

测试使用临时数据库，每个用例独立重建，不会污染 `instance/blog.sqlite3`。

## 10. 假设、边界与后续增量

沿用设计说明书附录 C：

1. 回复即评论，不另设板块；评论不分楼层嵌套。
2. 评论按发表时间倒序，每页 20 条。
3. 检索结果列表项为标题、作者、发表时间；检索结果暂不分页。
4. 会员账号预置，注册 / 找回密码不在范围内。
5. 登录失败次数不限。
6. 密码哈希存储，不存明文。

本实现额外提供、但不属于用例模型的内容：

- `POST /logout` 与页头“退出”按钮，便于演示多账号切换；
- 登录页演示账号提示；
- 贴心的 404/500 统一错误页与分页越界钳制。

已知边界：按课程范围未引入 CSRF 令牌、限流、审计日志等生产级防护；若要部署到公网，应补充这些机制并使用 HTTPS、强随机会话密钥。

后续增量（发帖、编辑/删除帖子、注册、管理端）不在当前范围；若扩展“发帖”，需在 `PostDAO` 增加 `save(post)` 并复用现有分层。
