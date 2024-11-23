from typing import List
from ninja import Router
from api.models import ModelQuestion, ModelExam
from api.schemas import QuestionSchema, QuestionCreateSchema
from django.db.models import Q

router = Router()

@router.post("/", response=QuestionSchema)
def create_question(request, data: QuestionCreateSchema):
    question = ModelQuestion.objects.create(exam_id=data.exam_id, text=data.text)
    return QuestionSchema.from_orm(question)

@router.get("/", response=List[QuestionSchema])
def list_question(request, query: str = None, exam_id: int = None, order_by: str = "created_at", page: int = 1, page_size: int = 10):
    questions = ModelQuestion.objects.all()


    if exam_id is not None:
        if not ModelExam.objects.filter(id=exam_id).exists():
            return {"detail": "Invalid exam ID"}, 400
        questions = questions.filter(exam_id=exam_id)

    if query:
        questions = questions.filter(Q(text__icontains=query))

    questions = questions.order_by(order_by)
    start = (page-1)*page_size
    end = start+page_size

    return questions[start:end]       