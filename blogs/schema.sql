-- 博客系统（浏览帖子）数据库结构
-- 对应设计说明书第 3 部分：member / post / comment

CREATE TABLE IF NOT EXISTS member (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS post (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    title      TEXT     NOT NULL,
    content    TEXT     NOT NULL,
    created_at DATETIME NOT NULL,
    author_id  INTEGER  NOT NULL REFERENCES member (id)
);

CREATE TABLE IF NOT EXISTS comment (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    content    TEXT     NOT NULL,
    created_at DATETIME NOT NULL,
    post_id    INTEGER  NOT NULL REFERENCES post (id) ON DELETE CASCADE,
    author_id  INTEGER  NOT NULL REFERENCES member (id)
);

-- 评论分页按“所属帖子 + 发表时间倒序”访问，建立复合索引。
CREATE INDEX IF NOT EXISTS idx_comment_post_created
    ON comment (post_id, created_at DESC);
