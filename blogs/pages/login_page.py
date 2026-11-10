"""登录页面（UC5 边界类）。"""

from __future__ import annotations

from typing import Optional

from flask import flash, redirect, render_template, request, url_for

from controllers.login_controller import LoginController


def safe_next_url(value: Optional[str]) -> str:
    """只接受站内相对路径，避免开放重定向。"""
    value = (value or "").strip()
    if not value or not value.startswith("/"):
        return ""
    if value.startswith("//") or "\\" in value or ":" in value:
        return ""
    return value


class LoginPage:
    """登录界面：展示表单、校验凭证、维护登录态。"""

    def __init__(self, login_controller: LoginController) -> None:
        self._login_controller = login_controller

    def show(self):
        """展示登录表单。"""
        next_url = safe_next_url(request.args.get("next"))
        return render_template(
            "login.html",
            error=None,
            username="",
            next_url=next_url,
        )

    def submit(self):
        """提交凭证：成功跳转 next 或检索页，失败留在本页提示（A-4）。"""
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        next_url = safe_next_url(request.form.get("next"))

        if self._login_controller.verify_credentials(username, password):
            flash("登录成功", "success")
            return redirect(next_url or url_for("search"))

        return render_template(
            "login.html",
            error="用户名或密码错误",
            username=username,
            next_url=next_url,
        )

    def logout(self):
        """退出登录（演示便利功能，不属于用例模型）。"""
        self._login_controller.logout()
        flash("已退出登录", "success")
        return redirect(url_for("search"))
