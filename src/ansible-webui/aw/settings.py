from pathlib import Path

from aw.config.main import config
from aw.config.hardcoded import LOGIN_PATH
from aw.utils.deployment import deployment_dev, deployment_prod
from aw.config.environment import get_aw_env_var

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = [
    BASE_DIR / 'aw' / 'templates/'
]

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
ROOT_URLCONF = 'aw.urls'
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
if deployment_prod():
    DB_FILE = Path(get_aw_env_var('db'))

    if not DB_FILE.parent.exists():
        try:
            DB_FILE.parent.mkdir(mode=0o750)

        except (OSError, FileNotFoundError):
            raise ValueError(f"Unable to created database directory: '{DB_FILE.parent}'")

    if DB_FILE.name.find('.') == -1:
        try:
            DB_FILE.mkdir(mode=0o750)

        except (OSError, FileNotFoundError):
            raise ValueError(f"Unable to created database directory: '{DB_FILE}'")

    if DB_FILE.is_dir():
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
