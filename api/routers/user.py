from ninja import Router
from django.contrib.auth.models import User
from django.db.models import Q
from api.models import ModelUserProfile
from api.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, ErrorSchema
from api.utils import is_authenticated, is_admin
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

router = Router(tags=["Users"])

@router.post("/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_user(request, payload: UserCreateSchema):
    """Create a new user with profile."""
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
def list_users(request, search: str = None, ordering: str = "id"):
    """List all users with optional search and ordering."""
    is_authenticated(request)
    is_admin(request)
    users = User.objects.all()
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))
    users = users.order_by(ordering)
    return [UserSchema.from_orm(user) for user in users]

@router.get("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_user_details(request, user_id: int):
    """Retrieve details of a specific user by ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="User not found"))
    return UserSchema.from_orm(user)

@router.patch("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def partial_update_user(request, user_id: int, data: UserUpdateSchema):
    is_authenticated(request)
    is_admin(request)  # Verifica permissão antes de validar os dados

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, {"detail": "User not found"})

    # Validação e atualização de dados
    for attr, value in data.model_dump(exclude_unset=True).items():
        if attr == "password":
            user.set_password(value)
        else:
            setattr(user, attr, value)

    # Atualizar o perfil (caso necessário)
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
    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, {"detail": "User not found"})

    # Atualizar os atributos do usuário
    for attr, value in data.model_dump(exclude_unset=True).items():
        if attr == "password":
            user.set_password(value)
        else:
            setattr(user, attr, value)

    user.save()

    # Atualizar o perfil
    profile_data = data.model_dump(exclude_unset=True)
    profile = user.profile
    profile.is_admin = profile_data.get("is_admin", profile.is_admin)
    profile.is_participant = profile_data.get("is_participant", profile.is_participant)
    profile.save()

    return UserSchema.from_orm(user)

@router.delete("/{user_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, user_id: int):
    """Delete a user by ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="User not found"))
    user.delete()
    return 204, None