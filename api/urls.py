from ninja import NinjaAPI
from api.routers.user import router as user_router
from api.routers.exam import router as exam_router
from api.routers.question import router as question_router

api = NinjaAPI()
api.add_router("/users", user_router)
api.add_router("/exams", exam_router)
api.add_router("/question", question_router)