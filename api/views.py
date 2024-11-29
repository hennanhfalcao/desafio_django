from ninja import NinjaAPI
from api.routers.auth import router as auth_router
from api.routers.user import router as user_router
from api.routers.exam import router as exam_router

api = NinjaAPI(
    title="Exam Management API",
    version="1.0",
    description="A RESTful API for managing exams, questions, choices, participants, and answers."
)

api.add_router("/auth", auth_router)
api.add_router("/users", user_router)
api.add_router("/exams", exam_router)



@api.get("/docs", include_in_schema=False)
def documentation(request):
    """
    Redireciona para a documentação gerada automaticamente.
    """
    return api.openapi_schema
