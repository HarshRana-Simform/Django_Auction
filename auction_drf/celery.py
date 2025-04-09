# auction_system/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_drf.settings')

app = Celery('auction_drf')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configuring the periodic task in Celery Beat
app.conf.beat_schedule = {
    'send-upcoming-auctions-email-every-day': {
        'task': 'core.tasks.send_upcoming_auctions_emails',
        # Sends email at 10 am every-day.
        'schedule': crontab(hour=10, minute=00),
    },
}
