from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from api.routers.user import router as user_router
from api.routers.exam import router as exam_router
from api.routers.question import router as question_router
from api.routers.choice import router as choice_router
from api.routers.participation import router as participation_router
from api.routers.answer import router as answer_router

api = NinjaExtraAPI()

api.register_controllers(NinjaJWTDefaultController)

api.add_router("/users", user_router)
api.add_router("/exams", exam_router)
api.add_router("/questions", question_router)
api.add_router("/choices", choice_router)
api.add_router("/participations", participation_router)
api.add_router("/answers", answer_router)