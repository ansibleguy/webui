from pathlib import Path
from os import environ

from aw.config.main import config
from aw.config.hardcoded import LOGIN_PATH, ENV_KEY_DB
from aw.utils.deployment import deployment_dev, deployment_prod

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = deployment_dev()
ALLOWED_HOSTS = ['*']
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'

INSTALLED_APPS = [
    'aw.apps.AwConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_user_agents',
    # styles
    'bootstrap5',
    'fontawesomefree',
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
ROOT_URLCONF = 'route'
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
DB_FILE = None
if deployment_prod():
    if ENV_KEY_DB in environ:
        DB_FILE = Path(environ[ENV_KEY_DB])
        if not DB_FILE.parent.exists():
            raise ValueError(f"Provided database directory does not exist: '{DB_FILE.parent}'")

    if DB_FILE is None:
        home_config = Path(environ['HOME']) / '.config'
        if home_config.is_dir():
            DB_FILE = home_config

    if DB_FILE is None:
        DB_FILE = Path(environ['HOME'])
        if not DB_FILE.is_dir():
            raise ValueError(f"Home directory does not exist: '{DB_FILE}'")

    DB_FILE = DB_FILE / 'aw.db'

else:
    DB_FILE = 'aw.dev.db' if deployment_dev() else 'aw.staging.db'
    DB_FILE = BASE_DIR / DB_FILE

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_FILE,
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
STATICFILES_DIRS = [BASE_DIR / 'aw' / 'static']
LOGIN_REDIRECT_URL = '/ui/'
LOGOUT_REDIRECT_URL = LOGIN_PATH
handler403 = 'aw.utils.handlers.handler403'
handler500 = 'aw.utils.handlers.handler500'

SECRET_KEY = config['_secret']
TIMEZONE = config['timezone']
