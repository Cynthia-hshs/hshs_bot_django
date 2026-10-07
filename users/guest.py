"""游客身份 —— 只活在浏览器签名 cookie 里，服务端不落库。

设计取舍：
  * 不用 Django session（默认后端会往 django_session 表写一行）
  * 不建 User 记录（避免用户表里攒下一堆游客）
  * 身份只用于「显示欢迎语」，所以放客户端、只签名不加密是安全的
  * 退出时删 cookie，或过期自动失效，服务端全程零写入
"""
import uuid

from django.conf import settings
from django.core import signing

COOKIE_NAME = "guest_id"
MAX_AGE = 60 * 60 * 24 * 7  # 7 天


def new_guest_name():
    """生成形如 hs_a3f9c2 的虚拟账号名"""
    return f"hs_{uuid.uuid4().hex[:6]}"


def get_guest_name(request):
    """读取当前游客名；没有 cookie 或签名被篡改都返回 None"""
    try:
        return request.get_signed_cookie(COOKIE_NAME)
    except (KeyError, signing.BadSignature):
        return None


def set_guest_cookie(response, name):
    """把游客名写进签名 cookie —— 没有这个 cookie 就不是游客"""
    response.set_signed_cookie(
        COOKIE_NAME,
        name,
        max_age=MAX_AGE,
        httponly=True,  # 禁止 JS 读取，降低 XSS 风险
        samesite="Lax",  # 防 CSRF
        # 线上（DEBUG=False）只在 HTTPS 下发送；本地是 http，必须关掉否则浏览器不存
        secure=not settings.DEBUG,
    )
    return response


def clear_guest_cookie(response):
    """退出：删掉 cookie。服务端本来就没存过，所以删完就彻底没了"""
    response.delete_cookie(COOKIE_NAME)
    return response
