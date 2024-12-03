from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.apps import apps  # Adicione esta importação
from django.conf import settings

# Define as configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_manager.settings')

app = Celery('exam_manager')

# Configurações do Celery no Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Faz autodiscovery das tarefas após o carregamento dos apps
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')