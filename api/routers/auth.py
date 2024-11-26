from ninja import Router
from ninja.responses import Response
from django.contrib.auth import authenticate
from api.utils import generate_jwt

router = Router(tags=["Auth"])

@router.post("/login/", response={200: dict, 400: dict})
def login(request, username: str, password: str):
    """
    Autentica o usuário e retorna um token JWT.
    """
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=400)
    token = generate_jwt(user)
    return {"token": token}