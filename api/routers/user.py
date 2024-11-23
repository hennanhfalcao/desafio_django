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
def list_users(request, query: str = None, order_by: str = "username", page: int = 1, page_size: int = 10):
    users = User.objects.all().select_related("profile")
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    
    users = users.order_by(order_by)
    start = (page - 1) * page_size
    end = start + page_size

    response = []

    for user in users[start:end]:
        profile = getattr(user, "profile", None)
        is_admin = profile.is_admin if profile else False
        is_participant = profile.is_participant if profile else not is_admin

        response.append({
            "id": user.id,
            "username": user.username,
            "email": user.email if user.email else "invalid@example.com",
            "is_admin": is_admin,
            "is_participant": is_participant,
        })
    return response