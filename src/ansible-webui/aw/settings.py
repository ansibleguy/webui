from pathlib import Path
from os import environ

try:
    from aw.config.main import config, VERSION

except ImportError:
    # pylint-django
    from aw.config.main import init_globals
    init_globals()
    from aw.config.main import config, VERSION


from aw.config.hardcoded import LOGIN_PATH, PORT_WEB
from aw.utils.deployment import deployment_dev, deployment_prod
from aw.config.environment import get_aw_env_var

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = [
    BASE_DIR / 'aw' / 'templates/'
]

DEBUG = deployment_dev()
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
    # api
    'rest_framework',
    'rest_framework_api_key',
    'drf_spectacular',
    # styles
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
    'django_auto_logout.middleware.auto_logout',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    f'http://localhost:{PORT_WEB}',
    'http://127.0.0.1',
    f'http://127.0.0.1:{PORT_WEB}',
]
if 'AW_PROXY' in environ:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ['*']
if 'AW_HOSTNAMES' in environ:
    for hostname in environ['AW_HOSTNAMES'].split(','):
        ALLOWED_HOSTS.append(hostname)
        CSRF_TRUSTED_ORIGINS.extend([
            f'http://{hostname}',
            f'https://{hostname}',
            f'http://{hostname}:{PORT_WEB}',
            f'https://{hostname}:{PORT_WEB}',
        ])

CSRF_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS
CORS_ORIGINS_WHITELIST = CSRF_TRUSTED_ORIGINS

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
            'debug': DEBUG,
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

    if DB_FILE.name.find('.') == -1 and not DB_FILE.exists():
        try:
            DB_FILE.mkdir(mode=0o750)

        except (OSError, FileNotFoundError):
            raise ValueError(f"Unable to created database directory: '{DB_FILE}'")

    if DB_FILE.is_dir():
        DB_FILE = DB_FILE / 'aw.db'

else:
    dev_db_file = 'aw.dev.db' if deployment_dev() else 'aw.staging.db'
    if 'AW_DB' in environ:
        DB_FILE = Path(get_aw_env_var('db'))
        if DB_FILE.is_dir():
            DB_FILE = DB_FILE / dev_db_file

    else:
        DB_FILE = dev_db_file
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

# Security
AUTO_LOGOUT = {
    'SESSION_TIME': config['session_timeout'],
}

# Internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'aw' / 'static']
LOGIN_REDIRECT_URL = '/ui/jobs/manage'  # todo: change to '/ui' once dashboard is implemented
LOGOUT_REDIRECT_URL = LOGIN_PATH
handler403 = 'aw.utils.handlers.handler403'
handler500 = 'aw.utils.handlers.handler500'

SECRET_KEY = config['secret']
TIMEZONE = config['timezone']

# api
API_KEY_CUSTOM_HEADER = 'HTTP_X_API_KEY'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        # 'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SPECTACULAR_SETTINGS = {
    # 'TITLE': 'AW API',
    # 'DESCRIPTION': 'Your project description',
    'VERSION': VERSION,
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SWAGGER_UI_FAVICON_HREF': STATIC_URL + 'img/ansible.svg',
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'apiKey': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-Api-Key',
            },
            # 'session': {
            #     'type': 'apiKey',
            #     'in': 'cookie',
            #    'name': 'sessionid',
            # },
        },
    },
    'SECURITY': [
        {'apiKey': []},
        # {'session': []},
    ],
    'SWAGGER_UI_SETTINGS': {
        'displayOperationId': False,
    },
}

if deployment_dev():
    SPECTACULAR_SETTINGS['SWAGGER_UI_SETTINGS']['persistAuthorization'] = True
