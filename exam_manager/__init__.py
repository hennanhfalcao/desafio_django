from __future__ import absolute_import, unicode_literals

# Configura o Celery como parte do projeto
from .celery import app as celery_app

__all__ = ('celery_app',)