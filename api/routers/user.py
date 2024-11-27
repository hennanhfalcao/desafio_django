from ninja import Router
from django.contrib.auth.models import User
from django.db.models import Q
from api.models import ModelUserProfile
from api.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, ErrorSchema
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset
from ninja.errors import HttpError


router = Router(tags=["Users"])

@router.post("/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_user(request, payload: UserCreateSchema):
    """Cria um usuário com perfil"""
    is_authenticated(request)
    is_admin(request)
    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        email=payload.email
    )
    ModelUserProfile.objects.create(
        user=user,
        is_admin=payload.is_admin,
        is_participant=payload.is_participant
    )
    return UserSchema.from_orm(user)

@router.get("/", response={200: list[UserSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_users(
    request, 
    query: str = None, 
    order_by: str = "id", 
    page: int = 1, 
    page_size: int = 10
):
    """
    Lista todos os usuários com busca, ordenação e paginação opcionais.
    """
    is_authenticated(request)
    is_admin(request)

    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))

    users = order_queryset(users, order_by)

    users = paginate_queryset(users, page, page_size)

    return [UserSchema.from_orm(user) for user in users]

@router.get("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_user_details(request, user_id: int):
    """Recupera detalhes do usuário por meio do ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="User not found"))
    return UserSchema.from_orm(user)

@router.patch("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def partial_update_user(request, user_id: int, data: UserUpdateSchema):
    """Atualiza parcialmente um usuário por meio do seu ID"""
    
    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, {"detail": "User not found"})

    for attr, value in data.model_dump(exclude_unset=True).items():
        if attr == "password":
            user.set_password(value)
        else:
            setattr(user, attr, value)

    profile_data = data.model_dump(exclude_unset=True)
    profile = user.profile
    if "is_admin" in profile_data:
        profile.is_admin = profile_data["is_admin"]
    if "is_participant" in profile_data:
        profile.is_participant = profile_data["is_participant"]
    user.save()
    profile.save()

    return UserSchema.from_orm(user)

@router.put("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def update_user(request, user_id: int, data: UserUpdateSchema):
    """Atualiza completamente um usuário por meio do seu ID"""
    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, {"detail": "User not found"})

    for attr, value in data.model_dump(exclude_unset=True).items():
        if attr == "password":
            user.set_password(value)
        else:
            setattr(user, attr, value)

    user.save()

    profile_data = data.model_dump(exclude_unset=True)
    profile = user.profile
    profile.is_admin = profile_data.get("is_admin", profile.is_admin)
    profile.is_participant = profile_data.get("is_participant", profile.is_participant)
    profile.save()

    return UserSchema.from_orm(user)

@router.delete("/{user_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, user_id: int):
    """Deleta um usuário pelo ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="User not found"))
    user.delete()
    return 204, None