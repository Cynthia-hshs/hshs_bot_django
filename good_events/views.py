from django.shortcuts import render


def index(request):
    """首页视图：显示祝福页面"""
    return render(request, "good_events/index.html")
