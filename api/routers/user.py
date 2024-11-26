from typing import List
from api.models import ModelUserProfile
from api.schemas import UserSchema, UserCreateSchema, UserUpdateSchema 
from django.contrib.auth.models import User
from django.db.models import Q
from ninja import Router,Schema
from ninja.responses import Response
from api.utils import is_authenticated, is_admin, paginate_and_order


router = Router()

class ErrorSchema(Schema):
    detail: str

@router.post("/", response={200: UserSchema, 400: ErrorSchema})
def create_user(request, payload: UserCreateSchema):

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


@router.get("/", response={200: List[UserSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_users(request, query: str = None, order_by: str = "username", page: int = 1, page_size: int = 10):
    """
    Lista todos os usuários com paginação e ordenação.
    """
    auth_error = is_authenticated(request)
    if auth_error:
        return Response(auth_error, status=auth_error[1])

    admin_error = is_admin(request)
    if admin_error:
        return Response(admin_error, status=admin_error[1])

    users = User.objects.all().select_related("profile")
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    
    users = paginate_and_order(users, order_by, page, page_size)
    return [UserSchema.from_orm(user) for user in users]

@router.get("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_user(request, user_id: int):
    """
    Obtém detalhes de um usuário específico.
    """
    auth_error = is_authenticated(request)
    if auth_error:
        return Response(auth_error, status=auth_error[1])

    if request.user.id != user_id:
        admin_error = is_admin(request)
        if admin_error:
            return Response(admin_error, status=admin_error[1])

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    return UserSchema.from_orm(user)


@router.put("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_user(request, user_id: int, payload: UserUpdateSchema):
    """
    Atualiza completamente um usuário e seu perfil.
    """
    auth_error = is_authenticated(request)
    if auth_error:
        return Response(auth_error, status=auth_error[1])

    admin_error = is_admin(request)
    if admin_error:
        return Response(admin_error, status=admin_error[1])

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    if payload.username:
        user.username = payload.username
    if payload.email:
        user.email = payload.email
    if payload.password:
        user.set_password(payload.password)
    user.save()

    profile = user.profile
    if payload.is_admin is not None:
        profile.is_admin = payload.is_admin
    if payload.is_participant is not None:
        profile.is_participant = payload.is_participant
    profile.save()

    return UserSchema.from_orm(user) 

@router.patch("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def partial_update_user(request, user_id: int, payload: UserUpdateSchema):
    """
    Atualiza parcialmente um usuário e seu perfil.
    """
    auth_error = is_authenticated(request)
    if auth_error:
        return Response(auth_error, status=auth_error[1])

    admin_error = is_admin(request)
    if admin_error:
        return Response(admin_error, status=admin_error[1])

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
    user.save()

    profile = user.profile
    if payload.is_admin is not None:
        profile.is_admin = payload.is_admin
    if payload.is_participant is not None:
        profile.is_participant = payload.is_participant
    profile.save()

    return UserSchema.from_orm(user)

@router.delete("/{user_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, user_id: int):
    """
    Deleta um usuário e seu perfil.
    """
    auth_error = is_authenticated(request)
    if auth_error:
        return Response(auth_error, status=auth_error[1])

    admin_error = is_admin(request)
    if admin_error:
        return Response(admin_error, status=admin_error[1])

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    user.delete()
    return 204, None  