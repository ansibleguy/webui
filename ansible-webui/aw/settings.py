from pathlib import Path
from os import path as os_path
from os import environ
from secrets import choice as random_choice
from string import digits, ascii_letters, punctuation

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve()


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap5',
    'bootstrap_datepicker_plus',
    'django_user_agents',
    'aw',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]
ROOT_URLCONF = 'urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
WSGI_APPLICATION = 'aw.main.app'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'aw.db',
        'OPTIONS': {
            'timeout': 10,
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 10,
        },
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os_path.join(BASE_DIR, 'static/')]
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
handler403 = 'aw.utils.handlers.handler403'
handler500 = 'aw.utils.handlers.handler500'

ENVIRON_FALLBACK = {
    'AW_TIMEZONE': 'GMT',
    'AW_SECRET': ''.join(random_choice(ascii_letters + digits + punctuation) for i in range(50)),
}

if 'AW_TIMEZONE' not in environ:
    AW_TIMEZONE = ENVIRON_FALLBACK['AW_TIMEZONE']

if 'AW_SECRET' not in environ:
    AW_SECRET = ENVIRON_FALLBACK['AW_SECRET']
