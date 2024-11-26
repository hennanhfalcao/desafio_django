from ninja import NinjaAPI
from api.routers.auth import router as auth_router
from api.routers.user import router as user_router
from api.routers.exam import router as exam_router
from api.routers.question import router as question_router
from api.routers.choice import router as choice_router
from api.routers.participation import router as participation_router
from api.routers.answer import router as answer_router

api = NinjaAPI(
    title="Exam Management API",
    version="1.0",
    description="A RESTful API for managing exams, questions, choices, participants, and answers."
)

api.add_router("/auth", auth_router)
api.add_router("/users", user_router)
api.add_router("/exams", exam_router)
api.add_router("/questions", question_router)
api.add_router("/choices", choice_router)
api.add_router("/participations", participation_router)
api.add_router("/answers", answer_router)


@api.get("/docs", include_in_schema=False)
def documentation(request):
    """
    Redireciona para a documentação gerada automaticamente.
    """
    return api.openapi_schema
