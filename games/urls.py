from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("", views.index, name="index"),
    # <slug> 会吃掉 /games/ 下的任何单词。以后要加固定子页（比如 /games/search/），
    # 把它写在上面那条之前就行 —— 路由是按顺序匹配的。
    path("<slug:slug>/", views.play, name="play"),
]
