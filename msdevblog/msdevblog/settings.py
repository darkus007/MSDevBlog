"""
Django settings for msdevblog project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from os import getenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'captcha',
    'taggit',
    'django.contrib.postgres',

    'blog.apps.BlogConfig',
    'members.apps.MembersConfig',
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

ROOT_URLCONF = 'msdevblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['members/templates/', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'blog.middlewares.categories',
                'blog.middlewares.new_posts',
                'blog.middlewares.tags_list',
            ],
        },
    },
]

WSGI_APPLICATION = 'msdevblog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('POSTGRES_DB', 'msdevblog'),
        'USER': getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': getenv('POSTGRES_HOST', 'localhost'),
        'PORT': getenv('POSTGRES_PORT', 5432),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================================= дополнительные настройки =================================

# Расширенная модель пользователя
AUTH_USER_MODEL = "members.AdvUser"


# Переадресацию после регистрации и выхода пользователя
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'blog:home'
LOGOUT_REDIRECT_URL = 'blog:home'


# настраиваем отправку писем
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # выводит в командной строке
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # отправляет на почтовый сервер
DEFAULT_FROM_EMAIL = 'flats@mail.ru'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
# EMAIL_HOST_USER = 'user'                                         # логин для SMTP-сервера, по умолчанию пустая строка
# EMAIL_HOST_PASSWORD = 'password'                                 # пароль для SMTP-сервера, по умолчанию пустая строка
ADMINS = [  # админы, которым будут отправлены письма методом mail_admins
    ('admin', 'admin@mail.ru'),
]
SERVER_EMAIL = 'flats_from@email.ru'  # адрес почты с которой будут отправлены письма
