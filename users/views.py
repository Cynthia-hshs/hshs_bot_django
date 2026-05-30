from django.shortcuts import render


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
