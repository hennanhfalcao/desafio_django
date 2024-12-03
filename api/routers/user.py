from ninja import Router
from django.db.models import Q
from api.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, ErrorSchema
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset, add_user_cache_key, clear_list_users_cache
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

router = Router(tags=["Users"])

@router.post("/", response={201: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_user(request, payload: UserCreateSchema):
    """Cria um usuário com perfil
    Para criar um usuário, primeiramente, crie um superuser com o comando:
    python manage.py createsuperuser.
    Insira os dados requisitados.
    Envie uma requisição POST para /api/token/ passando o username e a senha para obter o token de autenticação.
    Copie a resposta e utilize o token de acesso na cabeça da requisição.
    Authorization: Bearer -token-
    Aí sim será possível criar um usuário por meio dessa rota."""
    is_authenticated(request)
    is_admin(request)
    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        email=payload.email,
        is_admin=payload.is_admin,
        is_participant=payload.is_participant
    )
    clear_list_users_cache()
    return 201, UserSchema.model_validate(user)

@router.get("/", response={200: list[UserSchema], 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def list_users(
    request, 
    query: str = None, 
    order_by: str = "-username", 
    page: int = 1, 
    page_size: int = 10
):
    """
    Lista todos os usuários com busca, ordenação e paginação opcionais.
    É possível ordená-los por meio do campo username por meio da rota: /api/users/?order_by=-username
    A páginação é feita por meio da rota: /api/users/?page=2&page_size=10, em que os parâmetros page e page_size podem ser alterados.
    A busca por string é feita pelo campo text e pode ser testada acessando a rota: /api/users/?query=
    Apenas administradores podem ver a lista de usuários.
    """
    is_authenticated(request)
    is_admin(request)

    cache_key = f"list_users:{query}:{order_by}:{page}:{page_size}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data
    try:
        users = User.objects.all()
    except User.DoesNotExist:
        raise HttpError(404, "Nenhum usuário encontrado")
    
    
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))

    users = order_queryset(users, order_by)

    users = paginate_queryset(users, page, page_size)

    results = [UserSchema.model_validate(user) for user in users]
    cache.set(cache_key, results, timeout=300)
    add_user_cache_key(cache_key)
    return results

@router.get("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_user_details(request, user_id: int):
    """Recupera detalhes do usuário por meio do ID.
    Apenas administradores podem ver os detalhes de um usuário."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuário não encontrado")
    return UserSchema.model_validate(user)

@router.patch("/{user_id}/", response={200: UserSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def partial_update_user(request, user_id: int, payload: UserUpdateSchema):
    """Atualiza parcialmente um usuário por meio do seu ID"
    Apenas administradores podem atualizar um usuário."""
    
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
        clear_list_users_cache()
        return UserSchema.model_validate(user)        
    except User.DoesNotExist:
        raise HttpError(404, "Usuário não encontrado")

@router.delete("/{user_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_user(request, user_id: int):
    """Deleta um usuário pelo ID.
    Apenas administradores podem deletar usuários."""
    is_authenticated(request)
    is_admin(request)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuário não encontrado")
    user.delete()
    clear_list_users_cache()
    return 204, None