"""
本地开发配置 —— 从 .env 文件读取敏感信息
"""
import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *  # noqa

# 从项目根目录加载 .env 文件
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
