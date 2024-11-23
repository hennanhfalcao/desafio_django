from ninja import NinjaAPI
from api.routers.user import router as user_router
from api.routers.exam import router as exam_router

api = NinjaAPI()

api.add_router("/users", user_router)
api.add_router("/exams", exam_router)