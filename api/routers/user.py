from typing import List
from api.models import ModelUserProfile
from api.schemas import UserSchema, UserCreateSchema
from django.contrib.auth.models import User
from django.db.models import Q
from ninja import Router, Schema
from ninja.responses import Response

from rest_framework_simplejwt.tokens import AccessToken

router = Router()

class ErrorSchema(Schema):
    detail: str

@router.post("/", response={200: UserSchema, 400: ErrorSchema})
def create_user(request, payload: UserCreateSchema):

    if User.objects.filter(username=payload.username).exists():
        return Response({"detail": "Username already exists"}, status=400)

    try:
        user = User.objects.create_user(
            username=payload.username,
            password=payload.password,
            email=payload.email,
        )

        ModelUserProfile.objects.create(
            user=user,
            is_admin=payload.is_admin,
            is_participant=payload.is_participant,
        )
    except Exception as e:
        return Response({"detail": str(e)}, status=400)

    return UserSchema.from_orm(user)


@router.get("/", response={200: List[UserSchema], 403: ErrorSchema})
def list_users(request, query: str = None, order_by: str = "username", page: int = 1, page_size: int = 10):
    if not request.user.is_authenticated:
        return Response({"detail": "Unauthorized"}, status=403)
    
    if not request.user.is_admin:
        return Response({"detail": "Unauthorized - Not an admin"}, status=403)
    
    users = User.objects.all().select_related("profile")
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    
    users = users.order_by(order_by)
    start = (page - 1) * page_size
    end = start + page_size

    return [UserSchema.from_orm(user) for user in users[start:end]]


@router.get("/test-auth/", response={200: dict, 403: dict})
def test_auth(request):
    import logging
    logger = logging.getLogger('django')

    logger.info(f"Authorization Header: {request.headers.get('Authorization')}")

    if not request.user.is_authenticated:
        logger.warning("User is not authenticated")
        return Response({"detail": "Unauthorized"}, status=403)

    return {
        "user_id": request.user.id,
        "username": request.user.username,
        "is_admin": getattr(request.user.profile, "is_admin", None),
        "is_active": request.user.is_active
    }

"""@router.get("/decode-token/", response={200: dict, 403: dict})
def decode_token(request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        return {"detail": "Authorization header missing"}, 403

    try:
        token = authorization.split(" ")[1]  # Extrai o token do cabeçalho
        decoded = AccessToken(token)  # Decodifica o token
        user_id = decoded["user_id"]
        return {"user_id": user_id}
    except Exception as e:
        return {"detail": f"Token error: {str(e)}"}, 403"""

@router.get("/{user_id}/", response={200: UserSchema, 404: ErrorSchema})
def get_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    return UserSchema.from_orm(user)

@router.put("/{user_id}/", response={200: UserSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_user(request, user_id: int, payload: UserCreateSchema):
    if not request.user.is_authenticated or not request.user.is_admin:
        return Response({"detail": "Unauthorized"}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    user.username = payload.username
    user.email = payload.email
    if payload.password:
        user.set_password(payload.password)
    user.save()

    profile = user.profile
    profile.is_admin = payload.is_admin
    profile.is_participant = payload.is_participant
    profile.save()

    return UserSchema.from_orm(user)  

@router.patch("/{user_id}/", response={200: UserSchema, 403: ErrorSchema, 404: ErrorSchema})
def partial_update_user(request, user_id: int, payload: UserCreateSchema):
    if not request.user.is_authenticated or not request.user.is_admin:
        return Response({"detail": "Unauthorized"}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    if payload.username is not None:
        user.username = payload.username
    if payload.email is not None:
        user.email = payload.email
    if payload.password is not None:
        user.set_password(payload.password)

    profile = user.profile
    if payload.is_admin is not None:
        profile.is_admin = payload.is_admin
    if payload.is_participant is not None:
        profile.is_participant = payload.is_participant
    profile.save()
    user.save()

    return UserSchema.from_orm(user)

@router.delete("/{user_id}/", response={204: None, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, user_id: int):
    if not request.user.is_authenticated or not request.user.is_admin:
        return Response({"detail": "Unauthorized"}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    user.delete()
    return 204, None    