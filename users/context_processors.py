"""模板上下文处理器：把游客身份注入所有模板。

没有这个的话，每个视图都得手动 render(..., {"guest_name": ...})，
页面一多就是重复代码。注册在 settings.TEMPLATES 的 context_processors 里。
"""
from .guest import get_guest_name


def guest(request):
    """所有模板都能直接用 {{ guest_name }}，未登录时为 None"""
    return {"guest_name": get_guest_name(request)}
