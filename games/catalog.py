"""游戏清单 —— 全站小游戏的唯一数据源，加新游戏只改这个文件。

一份产物 = 一个目录，永远只有一份，可以被多个列表项引用。
一条记录 = 一个 URL（/games/<slug>/）+ 一个标题 + 它指向哪份产物。

    static/games/<dir>/
    ├── Build/           打包产物（Unity WebGL 的 WebGL.data / .framework.js / .loader.js / .wasm）
    ├── TemplateData/    打包产物附带的模板资源（style.css 及配套图片）
    └── cover.svg        列表页用的方形封面

<dir> 默认就等于记录的 slug，所以「一款游戏一份产物」时什么都不用写。
要让多个入口共用同一份产物，给后加的记录传 assets=<dir> —— 目录不会被复制。

slug（URL 身份）和 <dir>（产物位置）是分开的，这点是刻意的：
改 URL 不用挪目录，也就不会牵动 git 历史和 LFS 里的路径。

路径统一在 _game() 里由目录名推导，所以目录里的东西换了不用改代码；
换封面直接替换 cover.svg 即可（列表页是 aspect-ratio:1/1 + object-fit:cover，非方形图会自动裁切）。

当前这款「合成一只白色QvQ」来自 Unity 工程 D:\\Project\\UnityProj\\baiseqvq 的 WebGL 导出
（未压缩构建 —— wasm 是裸的，不是 .unityweb，所以 nginx 不需要任何 Content-Encoding 配置）。
重新导出后，把新的 Build/ 和 TemplateData/ 覆盖到 static/games/baiseqvq/ 下就行，模板不用动。

注意：别把 Unity 导出的 index.html 复制进来。那等于多开一个绕过站点导航的公开入口
（/static/games/baiseqvq/index.html 谁都能直接访问）。本站的播放页是 templates/game_play.html，
由 games.views.play 渲染，它会用 {% static %} 拼出绝对路径喂给 Unity 的 loader。
"""


def _game(slug, title, assets=None, build_prefix="WebGL", version="1.0"):
    """补全由产物目录名派生的静态路径。

    手写这些路径迟早会写错一半或者改一半，统一在这里生成。

    assets 是产物目录名（对应 static/games/<assets>/），默认等于本记录的 slug。
    一款游戏一份产物时不用传；多个列表项要指向同一份产物时，在这些记录上
    写同一个 assets —— 目录仍然只有一份，不会被复制。

    build_prefix 是 Unity 导出时给产物取的名字（导出目录里那四个 WebGL.data /
    .framework.js / .loader.js / .wasm 的前缀）。换名字重新导出的话，改这一个参数就行。
    """
    base = f"games/{assets or slug}"
    return {
        "slug": slug,
        "title": title,
        "version": version,
        "build_prefix": build_prefix,
        "cover": f"{base}/cover.svg",                  # 列表页方形封面
        "build_dir": f"{base}/Build",                  # Unity Build 目录
        "template_data": f"{base}/TemplateData",       # Unity 模板资源目录
        "streaming_assets": f"{base}/StreamingAssets",  # 目前没有这个目录，但路径语义要对
    }


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
