from django.shortcuts import redirect, render

from .guest import clear_guest_cookie, new_guest_name, set_guest_cookie


def login_view(request):
    """登录页视图（仅界面，后端逻辑后续实现）"""
    return render(request, "users/login.html")


def register_view(request):
    """注册页视图（仅界面，后端逻辑后续实现）"""
    return render(request, "users/register.html")


def forgot_password_view(request):
    """忘记密码 - 第一步：邮箱验证（仅界面）"""
    return render(request, "users/forgot_password.html")


def set_password_view(request):
    """设置密码 - 第二步：注册/重置共用（仅界面）"""
    return render(request, "users/set_password.html")


def guest_login(request):
    """游客登录：生成 hs_xxxxxx 虚拟账号名，写进签名 cookie 后进主页。

    不建 User 记录、不写 session，服务端零留存；退出或 7 天后自动消失。
    """
    return set_guest_cookie(redirect("good_events:home"), new_guest_name())


def guest_logout(request):
    """游客退出：删掉 cookie 就彻底没了，回主页"""
    return clear_guest_cookie(redirect("good_events:home"))
