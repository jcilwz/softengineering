"""登录控制器（UC5）。

登录态由 Flask session 承载：member_id / member_name。
"""

from __future__ import annotations

from typing import Optional

from flask import session

from dao.member_dao import MemberDAO


class LoginController:
    """凭证校验与登录态维护。"""

    SESSION_MEMBER_ID = "member_id"
    SESSION_MEMBER_NAME = "member_name"

    def __init__(self, member_dao: MemberDAO) -> None:
        self._member_dao = member_dao

    def verify_credentials(self, username: str, password: str) -> bool:
        """校验用户名与密码；成功时建立登录态并返回 True。"""
        username = (username or "").strip()
        if not username or not password:
            return False

        member = self._member_dao.find_by_username(username)
        if member is None or not member.verify_password(password):
            return False

        session[self.SESSION_MEMBER_ID] = member.id
        session[self.SESSION_MEMBER_NAME] = member.username
        return True

    def is_logged_in(self) -> bool:
        """判定当前登录状态（业务规则 B-1：系统自动判定）。"""
        return self.current_member_id is not None

    @property
    def current_member_id(self) -> Optional[int]:
        """当前会员 ID；未登录返回 None。"""
        value = session.get(self.SESSION_MEMBER_ID)
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @property
    def current_member_name(self) -> Optional[str]:
        """当前会员用户名；未登录返回 None。"""
        value = session.get(self.SESSION_MEMBER_NAME)
        return str(value) if value is not None else None

    def logout(self) -> None:
        """清除登录态（演示便利功能，不属于用例模型）。"""
        session.pop(self.SESSION_MEMBER_ID, None)
        session.pop(self.SESSION_MEMBER_NAME, None)
