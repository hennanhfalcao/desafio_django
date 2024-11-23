from typing import List
from ninja import Router
from api.models import ModelExam
from api.schemas import ExamCreateSchema, ExamSchema
from django.db.models import Q

router = Router()

@router.post("/", response=ExamSchema)
def create_exam(request, data: ExamCreateSchema):
    exam = ModelExam.objects.create(name=data.name, created_by=request.user)
    return ExamSchema.from_orm(exam)

@router.get("/", response=List[ExamSchema])
def list_exams(request, query: str = None, order_by: str = "-created_at", page: int = 1, page_size: int = 10):
    exams = ModelExam.objects.all()
    if query:
        exams = exams.filter(Q(name__icontains=query))
    exams = exams.order_by(order_by) 
    start = (page-1)*page_size
    end = start + page_size
    return exams[start:end]