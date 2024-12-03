from ninja import NinjaAPI
from api.routers.user import router as user_router
from api.routers.exam import router as exam_router
from api.routers.question import router as question_router
from api.routers.answer import router as answer_router
from api.routers.ranking import router as ranking_router

api = NinjaAPI(
    title="Exams Management API",
    version="1.0",
    description="API RESTful para gerenciamento de provas de múltipla escolha. Consulte os Schemas para detalhes de como devem ser as requisições.",
)

api.add_router("/users", user_router)
api.add_router("/exams", exam_router)
api.add_router("/questions", question_router)
api.add_router("/answers", answer_router)
api.add_router("/rankings", ranking_router)


@api.get("/docs", include_in_schema=False)
def documentation(request):
    """
    Redireciona para a documentação gerada automaticamente.
    """
    return api.openapi_schema
