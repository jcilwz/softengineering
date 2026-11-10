"""数据访问层（DAO）。"""

from dao.comment_dao import CommentDAO
from dao.member_dao import MemberDAO
from dao.post_dao import PostDAO

__all__ = ["PostDAO", "CommentDAO", "MemberDAO"]
