import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=30),  # Expira em 30 minutos
        'iat': datetime.now(tz=timezone.utc),  # Emitido em
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token.decode('utf-8') if isinstance(token, bytes) else token

def decode_jwt(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido")
    
def is_authenticated(request):
    if isinstance(request.user, AnonymousUser):
        raise HttpError(401, "Authentication required")

def is_admin(request):
    if not getattr(request.user, "is_admin", False):
        raise HttpError(403, "Permission denied")

def order_queryset(queryset, order_by):
    """
    Ordena o queryset com base em um campo fornecido.
    """
    return queryset.order_by(order_by)

def paginate_queryset(queryset, page, page_size):
    """
    Pagina o queryset com base no número da página e no tamanho da página.
    """
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]


CACHE_KEY_SET = "list_exam_keys"

def add_cache_key(key):
    """Adiciona uma chave ao conjunto de chaves do cache."""
    keys = cache.get(CACHE_KEY_SET, set())
    keys.add(key)
    cache.set(CACHE_KEY_SET, keys, timeout=None)

def clear_list_exams_cache():
    """Limpa todas as chaves relacionadas ao cache de listagem de provas."""
    keys = cache.get(CACHE_KEY_SET, set())
    for key in keys:
        cache.delete(key)
    cache.delete(CACHE_KEY_SET)