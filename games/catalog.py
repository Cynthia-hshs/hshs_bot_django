"""游戏清单 —— 全站小游戏的唯一数据源，加新游戏只改这个文件。

一份产物 = 一个目录，永远只有一份，可以被多个列表项引用。
一条记录 = 一个 URL（/games/<slug>/）+ 一个标题 + 它指向哪份产物。

    static/games/<dir>/
    ├── Build/           打包产物，四个文件名都带哈希（下面解释）
    ├── TemplateData/    打包产物附带的模板资源（目前只用到两张进度条 PNG）
    └── cover.svg        列表页用的方形封面

<dir> 默认就等于记录的 slug，所以「一款游戏一份产物」时什么都不用写。
要让多个入口共用同一份产物，给后加的记录传 assets=<dir> —— 目录不会被复制。

slug（URL 身份）和 <dir>（产物位置）是分开的，这点是刻意的：
改 URL 不用挪目录，也就不会牵动 git 历史和 LFS 里的路径。

**四个产物的文件名不在这里拼**，由 resolve_build() 在请求期扫目录按扩展名认。
Unity 那边开了 nameFilesAsHashes，重新导出后四个名字全变，写死就等于每次都要改代码。
（哈希不是随便选的，是 Unity 侧刻意的：文件名跨构建恒定的话，浏览器会一直喂你旧的 wasm。
我们这边同样吃这个亏 —— static 由 nginx 直接伺服，缓存一样会命中。）
换封面直接替换 cover.svg 即可（列表页是 aspect-ratio:1/1 + object-fit:cover，非方形图会自动裁切）。

当前这款「合成一只白色QvQ」来自 Unity 工程 D:\\Project\\UnityProj\\baiseqvq 的 WebGL 导出
（未压缩构建 —— wasm 是裸的，不是 .unityweb，所以 nginx 不需要任何 Content-Encoding 配置）。

重新导出的接入流程，别照搬「覆盖 Build/ 和 TemplateData/ 就行」：

  1. 【先删后拷】先删掉 static/games/baiseqvq/Build/ 里上一次的四个产物，再复制新的四个进去。
     顺序不能反 —— 同一类产物留了两份（比如两个 .wasm），resolve_build() 会直接报错，
     而不是随便挑一个。宁可页面 404，也不要静默用错包。
  2. TemplateData/ 现在只有两张进度条 PNG 还被播放页用到
     （progress-bar-empty-dark.png / progress-bar-full-dark.png）。
     新导出里那份 style.css 是【整页样式】（html,body{overflow:hidden;height:100%} 加上
     #unity-container{position:fixed;inset:0}），引进来会盖住全站导航、锁死所有页面的滚动。
     所以播放页既不 link 它，也不把它贴进 <style>（后者会因为里面的相对 url() 全部 404）。
     播放页的样式全写在 templates/game_play.html 里，要引图就走 {% static %} 出绝对路径。
  3. 【别复制 Unity 导出的 index.html】那等于多开一个绕过站点导航的公开入口
     （/static/games/baiseqvq/index.html 谁都能直接访问）。本站的播放页是
     templates/game_play.html，由 games.views.play 渲染。
     ServiceWorker.js / manifest.webmanifest 也不复制 —— 本站不接 PWA。
"""

from pathlib import Path

from django.conf import settings

# 产物扩展名 → resolve_build() 返回字典里的键名。
# 四个后缀互不为后缀（.framework.js / .loader.js 都以 .js 结尾，但谁也不是谁的后缀；
# .data / .wasm 同理），所以顺序其实无所谓，按「长的在前」排只是为了读起来放心。
_BUILD_SUFFIXES = (
    (".framework.js", "framework"),
    (".loader.js", "loader"),
    (".data", "data"),
    (".wasm", "code"),
)

# Unity 压缩导出时会在上面每个后缀后再挂一层 .unityweb（WebGL.wasm.unityweb 这种）。
# 当前工程 Compression = Disabled，用不上；提前认是为了将来真开压缩时这里零改动 ——
# 但压缩产物会让 nginx 那条 wasm MIME 规则失效，真要用得连部署侧一起改（见 CLAUDE.md）。
_COMPRESSED_SUFFIX = ".unityweb"

# STATICFILES_DIRS 的源目录，和 settings/base.py 里那条保持一致。
# 不走 staticfiles 的 finders：那套是「给一个确切路径、问它文件在不在」，
# 而这里要的是「列出目录里有什么」，直接读文件系统更直白。
_STATIC_SOURCE_DIR = Path(settings.BASE_DIR) / "static"


class BuildNotFound(Exception):
    """产物目录缺失、产物不齐，或同一类产物不唯一。

    ⚠️ 只能在【访问某个游戏时】抛出，绝不能在 import 期抛 ——
    catalog 被 games.urls → games.views 链式导入，而 BOT_Django/urls.py
    在进程启动时就 include 它。模块顶层一抛异常，整站（含 admin 和主页）都起不来，
    不只是这一个游戏页。所以扫描放在 resolve_build() 里，由视图在请求期调用。
    """


def _game(slug, title, assets=None, version="1.0"):
    """补全由产物目录名派生的静态路径。

    手写这些路径迟早会写错一半或者改一半，统一在这里生成。
    四个产物的文件名不在这里拼（带哈希、每次重导出都变），由 resolve_build() 扫目录认。

    assets 是产物目录名（对应 static/games/<assets>/），默认等于本记录的 slug。
    一款游戏一份产物时不用传；多个列表项要指向同一份产物时，在这些记录上
    写同一个 assets —— 目录仍然只有一份，不会被复制。
    """
    base = f"games/{assets or slug}"
    return {
        "slug": slug,
        "title": title,
        "version": version,
        "cover": f"{base}/cover.svg",                  # 列表页方形封面
        "build_dir": f"{base}/Build",                  # Unity Build 目录
        "template_data": f"{base}/TemplateData",       # Unity 模板资源目录（进度条 PNG）
        "streaming_assets": f"{base}/StreamingAssets",  # 目前没有这个目录，但路径语义要对
    }


def resolve_build(game):
    """扫描产物目录，返回四个产物的【静态相对路径】。

    返回值每一项都能直接喂给 {% static %}：

        {"dir":       "games/baiseqvq/Build",
         "loader":    "games/baiseqvq/Build/7a2dbded….loader.js",
         "framework": "games/baiseqvq/Build/60e09ee5….framework.js",
         "data":      "games/baiseqvq/Build/9c326922….data",
         "code":      "games/baiseqvq/Build/6aac017c….wasm"}

    按扩展名认文件，所以重新导出换了哈希名不用动任何代码。

    目录不存在 / 某类产物没找到 / 同一类找到多个 → BuildNotFound，
    文案里带上是哪个游戏、缺什么、怎么办。这里【故意不做缓存】：
    重导出后要能改完文件就生效，不用重启进程。
    """
    rel_dir = game["build_dir"]                       # 形如 games/<dir>/Build
    abs_dir = _STATIC_SOURCE_DIR / rel_dir

    if not abs_dir.is_dir():
        raise BuildNotFound(
            f"找不到游戏产物目录 static/{rel_dir}/（{game['title']}）——"
            f"确认 Build/ 已经从 Unity 导出目录复制过来了。"
        )

    # 键名 -> 命中的文件名列表。命中多个也要记下来，留到下面统一报错：
    # 静默挑一个的话，旧产物没删干净时页面会用错包，而且完全没有迹象。
    hits = {}
    for entry in sorted(abs_dir.iterdir()):
        if not entry.is_file():
            continue
        for suffix, key in _BUILD_SUFFIXES:
            if entry.name.endswith((suffix, suffix + _COMPRESSED_SUFFIX)):
                hits.setdefault(key, []).append(entry.name)
                break

    problems = []
    for suffix, key in _BUILD_SUFFIXES:
        names = hits.get(key, [])
        if not names:
            problems.append(f"没有 {suffix} 产物")
        elif len(names) > 1:
            problems.append(
                f"{suffix} 产物不唯一：{'、'.join(names)}（上一次的没删干净？）"
            )
    if problems:
        raise BuildNotFound(
            f"游戏「{game['title']}」的产物不可用（static/{rel_dir}/）："
            + "；".join(problems)
            + "。清空该目录后只放一份导出产物，再试。"
        )

    build = {"dir": rel_dir}
    for _, key in _BUILD_SUFFIXES:
        build[key] = f"{rel_dir}/{hits[key][0]}"
    return build


# 列表顺序就是列表页的显示顺序
GAMES = [
    # ⚠️ 下面 5 条里，有 4 条是【临时占位】，只为预览列表页多卡片的排版效果。
    # 它们共用第一份产物（assets="baiseqvq"），所以没有复制任何文件。
    #
    # 有真游戏接入时，把每条改成自己的 slug / title，并【删掉 assets】——
    # 不传 assets 时产物目录默认就等于 slug，天生一条记录一份产物。
    # 部署前记得把这批占位记录删掉，否则线上会显示 5 张一模一样的卡片。
    _game(
        slug="baiseqvq",
        title="合成一只白色QvQ",
    ),
    _game(slug="placeholder-2", title="合成一只白色QvQ", assets="baiseqvq"),
    _game(slug="placeholder-3", title="合成一只白色QvQ", assets="baiseqvq"),
    _game(slug="placeholder-4", title="合成一只白色QvQ", assets="baiseqvq"),
    _game(slug="placeholder-5", title="合成一只白色QvQ", assets="baiseqvq"),
]


def get_game(slug):
    """按 slug 取一款游戏；没有就返回 None，由视图转成 404"""
    return next((g for g in GAMES if g["slug"] == slug), None)
