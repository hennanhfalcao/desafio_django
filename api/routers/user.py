from typing import List
from ninja import Router
from api.models import ModelUserProfile
from api.schemas import UserCreateSchema, UserSchema
from django.contrib.auth.models import User
from django.db.models import Q

router = Router()


@router.post("/", response=UserSchema)
def create_user(request, data: UserCreateSchema):
    user = User.objects.create_user(
        username=data.username,
        password=data.password,
        email=data.email
    )
    ModelUserProfile.objects.create(
        user=user,
        is_admin=data.is_admin,
        is_participant=data.is_participant
    )
    return UserSchema.from_orm(user)

@router.get("/", response=List[UserSchema])
def list_users(request, query: str = None, page: int = 1, page_size: int = 10):
    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    start = (page - 1) * page_size
    end = start + page_size
    return users[start:end]