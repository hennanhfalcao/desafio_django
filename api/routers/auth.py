from ninja import Router, Schema
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from api.utils import generate_jwt

router = Router(tags=["Authentication"])

class LoginSchema(Schema):
    username: str
    password: str

@router.post("/login/", response={200: dict, 401: dict})
def login(request, payload: LoginSchema):
    """
    Endpoint para autenticação de usuários.
    """
    user = authenticate(username=payload.username, password=payload.password)
    if not user:
        return HttpError(401, {"detail": "Invalid username or password"})

    token = generate_jwt(user)
    return {"access_token": token}