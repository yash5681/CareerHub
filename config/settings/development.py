import socket
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.loca.lt', 'http://*.loca.lt', 'http://127.0.0.1:8000', 'http://localhost:8000']

# Check if PostgreSQL service is reachable
def is_db_reachable(host, port):
    try:
        s = socket.create_connection((host, int(port)), timeout=1.5)
        s.close()
        return True
    except OSError:
        return False

# Use PostgreSQL if port 5432 is responding; otherwise, graceful local fallback in dev mode
if not is_db_reachable(DATABASES['default']['HOST'], DATABASES['default']['PORT']):
    # Only fallback in local dev if PostgreSQL server is not running
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# Development email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
