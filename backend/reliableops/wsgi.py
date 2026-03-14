"""WSGI config for reliableops project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reliableops.settings')
application = get_wsgi_application()
