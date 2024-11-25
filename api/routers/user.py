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

@router.get("/{user_id}/", response=UserSchema)
def get_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"detail":"User not found"}, 404
    profile = user.profile
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": profile.is_admin,
        "is_participant": profile.is_participant,
    }

@router.put("/{user_id}/", response=UserSchema)
def update_user(request, user_id: int, data: UserCreateSchema):
    try:
        user=User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"detail":"User not found"}, 404

    user.username = data.username
    user.email = data.email
    if data.password:
        user.set_password(data.password)
    user.save()

    profile = user.profile
    profile.is_admin = data.is_admin
    profile.is_participant = data.is_participant
    profile.save()


    return UserSchema.from_orm(user)   

@router.patch("/{user_id}/", response=UserSchema)
def partial_update_user(request, user_id: int, data: UserCreateSchema):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"detail":"User not found"}, 404
    
    if data.username is not None:
        user.username = data.username
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.set_password(data.password)
    user.save()

    profile = user.profile
    if data.is_admin is not None:
        profile.is_admin=data.is_admin
    if data.is_participant is not None:
        profile.is_participant = data.is_participant
    profile.save()

    return UserSchema.from_orm(user)            

@router.delete("/{user_id}/", response={204:None})
def delete_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"detail":"User not found"}, 404
    user.delete()
    return 204, None    