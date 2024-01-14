from os import environ

from django.core.wsgi import get_wsgi_application

environ.setdefault('DJANGO_SETTINGS_MODULE', 'aw.settings')
environ['PYTHONIOENCODING'] = 'utf8'
environ['PYTHONUNBUFFERED'] = '1'

app = get_wsgi_application()
