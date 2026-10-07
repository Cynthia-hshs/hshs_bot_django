from django.shortcuts import render


def home(request):
    """主页"""
    return render(request, "home.html")


def page1(request):
    """示例页 一"""
    return render(request, "page1.html")


def page2(request):
    """示例页 二"""
    return render(request, "page2.html")


def page3(request):
    """示例页 三"""
    return render(request, "page3.html")
