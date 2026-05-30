"""
生产配置 —— 部署时使用

使用方式：
    export DJANGO_SETTINGS_MODULE=BOT_Django.settings.production

注意：请将 SECRET_KEY 和数据库密码通过环境变量传入，不要硬编码。
"""
from .base import *  # noqa

# 必须通过环境变量设置密钥，不可写在代码里
import os

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# 生产环境建议使用 PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ['DB_NAME'],
#         'USER': os.environ['DB_USER'],
#         'PASSWORD': os.environ['DB_PASSWORD'],
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }
