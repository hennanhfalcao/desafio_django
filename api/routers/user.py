from ninja import Router
from django.db.models import Q
from api.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, ErrorSchema
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset
from ninja.errors import HttpError
from django.contrib.auth import get_user_model

User = get_user_model()

router = Router(tags=["Users"])

@router.post("/", response={201: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_user(request, payload: UserCreateSchema):
    """Cria um usuário com perfil"""
    is_authenticated(request)
    is_admin(request)
    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        email=payload.email,
        is_admin=payload.is_admin,
        is_participant=payload.is_participant
    )
    return 201, UserSchema.model_validate(user)

@router.get("/", response={200: list[UserSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_users(
    request, 
    query: str = None, 
    order_by: str = "-username", 
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

    return [UserSchema.model_validate(user) for user in users]

@router.get("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_user_details(request, user_id: int):
    """Recupera detalhes do usuário por meio do ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuário não encontrado")
    return UserSchema.model_validate(user)

@router.patch("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def partial_update_user(request, user_id: int, payload: UserUpdateSchema):
    """Atualiza parcialmente um usuário por meio do seu ID"""
    
    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=user_id)
        for attr, value in payload.model_dump(exclude_unset=True).items():
            if attr == "password":
                user.set_password(value)
            else:
                setattr(user, attr, value)
        user.save()
        return UserSchema.model_validate(user)        
    except User.DoesNotExist:
        raise HttpError(404, "Usuário não encontrado")

@router.delete("/{user_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, user_id: int):
    """Deleta um usuário pelo ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")
    user.delete()
    return 204, None