from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Define o módulo padrão de configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Cria a instância do Celery
app = Celery('core')

# Lê configurações do Django e as aplica no Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre tarefas automaticamente nos apps instalados
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')