import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from ninja.errors import HttpError

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
    if not getattr(request.user.profile, "is_admin", False):
        raise HttpError(403, "Permission denied")

def paginate_and_order(queryset, order_by, page, page_size):
    queryset = queryset.order_by(order_by)
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]