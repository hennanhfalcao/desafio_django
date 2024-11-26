import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(minutes=30),  # Expira em 30 minutos
        'iat': datetime.utcnow(),  # Emitido em
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido")
    
def is_authenticated(request):
    if isinstance(request.user, AnonymousUser):
        return {"detail": "Authentication required"}, 401
    return None

def is_admin(request):
    if not getattr(request.user.profile, "is_admin", False):
        return {"detail": "Permission denied"}, 403
    return None

def paginate_and_order(queryset, order_by, page, page_size):
    queryset = queryset.order_by(order_by)
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]