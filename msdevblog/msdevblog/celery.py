"""
To run Celery
celery -A msdevblog worker -l INFO

To start the celery beat service
celery -A msdevblog beat -l INFO
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msdevblog.settings')
app = Celery('msdevblog')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
