from pathlib import Path
import os
import environ

# 1. Ініціалізація django-environ для читання змінних з Docker
env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Читаємо SECRET_KEY та DEBUG з оточення Docker
SECRET_KEY = env.str('SECRET_KEY', default='django-insecure-dev-key-12345')
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['*']


# 2. Модульна архітектура проєкту згідно з Розділом 5 вашого ТЗ
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонні бібліотеки
    'rest_framework',
    'django_filters',
    'drf_spectacular',

    # Наші модулі магазину
    'users.apps.UsersConfig',
    'products.apps.ProductsConfig',
    'orders.apps.OrdersConfig',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Папка для HTML-шаблонів
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# 3. Налаштування підключення до PostgreSQL в Docker згідно з ТЗ
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://shop_user:shop_secure_pass@db:5432/hop_barley_db')
}


# Валідація паролів
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Мова та час
LANGUAGE_CODE = 'uk-ua'
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True


# 4. Налаштування статичних файлів та зображень товарів (Static & Media)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# 5. Активація кастомної моделі користувача згідно з ТЗ
AUTH_USER_MODEL = 'users.User'

# Унікальний ідентифікатор кошика в сесіях користувачів
CART_SESSION_ID = 'cart'

# Налаштування авторизації для Django REST Framework згідно з ТЗ
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Вказуємо drf-spectacular головним генератором схем OpenAPI
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

from datetime import timedelta

# Налаштування часу життя access та refresh токенів згідно з ТЗ 3.7
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',), # Токени передаються як "Bearer <token>"
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Hop & Barley API',
    'DESCRIPTION': 'Інтерактивна документація інтернет-магазину на Django/DRF згідно з ТЗ',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}