import logging

from django.http import Http404
from django.shortcuts import render

from .catalog import GAMES, BuildNotFound, get_game, resolve_build

logger = logging.getLogger(__name__)


def index(request):
    """小游戏列表页 —— 方形封面网格，点进对应的播放页"""
    return render(request, "games.html", {"games": GAMES})


def play(request, slug):
    """游戏播放页 —— 按 slug 套对应的外壳（目前只有 Unity WebGL 一种）"""
    game = get_game(slug)
    if game is None:
        raise Http404(f"没有这个游戏：{slug}")

    try:
        build = resolve_build(game)
    except BuildNotFound as exc:
        # 产物缺失是【运维问题】，不是访客输错了 URL：
        # 记一条 error 进日志（DEBUG=False 时这是唯一能看到中文详情的地方），
        # 页面本身给干净的 404，不把栈曝给访客。
        # DEBUG=True（本地）时，404 调试页会直接把这段中文显示出来，方便定位。
        logger.error("游戏 %s 的产物加载失败：%s", slug, exc)
        raise Http404(str(exc)) from exc

    return render(request, "game_play.html", {"game": game, "build": build})
