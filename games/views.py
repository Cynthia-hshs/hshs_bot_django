from django.http import Http404
from django.shortcuts import render

from .catalog import GAMES, get_game


def index(request):
    """小游戏列表页 —— 方形封面网格，点进对应的播放页"""
    return render(request, "games.html", {"games": GAMES})


def play(request, slug):
    """游戏播放页 —— 按 slug 套对应的外壳（目前只有 Unity WebGL 一种）"""
    game = get_game(slug)
    if game is None:
        raise Http404(f"没有这个游戏：{slug}")
    return render(request, "game_play.html", {"game": game})
