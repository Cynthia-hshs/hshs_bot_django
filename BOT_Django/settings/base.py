"""
Django 基础配置 —— 所有环境共享的公共配置
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 自定义应用
    'good_events',
    'users',
    'games',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BOT_Django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 项目级模板目录：base.html 与全站页面放这里
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 把游客身份注入所有模板，模板里直接写 {{ guest_name }} 即可
                'users.context_processors.guest',
            ],
        },
    },
]

WSGI_APPLICATION = 'BOT_Django.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
# collectstatic 的输出目录，由 Nginx 的 location /static/ 直接伺服
STATIC_ROOT = BASE_DIR / 'staticfiles'
# 项目级静态资源目录（公共 CSS 等），collectstatic 时会收集到 STATIC_ROOT
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── 部署相关：站点跑在 Nginx 反代后面 ──────────────────────────────
# Nginx 通过 X-Forwarded-Proto 告知原始请求协议，Django 靠它判断
# request.is_secure()。缺了这项，Django 会认为所有请求都是 HTTP，
# 导致 /admin/ 登录时报 CSRF 失败。
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Django 4.0+ 要求显式声明信任的 HTTPS 来源，否则跨源 POST 会被 CSRF 拦截
CSRF_TRUSTED_ORIGINS = [
    'https://lelehorse.cn',
    'https://www.lelehorse.cn',
]
