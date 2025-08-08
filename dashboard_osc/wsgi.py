"""
WSGI config for dashboard_osc project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')

application = get_wsgi_application()
