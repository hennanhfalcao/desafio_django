from typing import List
from ninja import Router
from api.models import ModelExam
from api.schemas import ExamCreateSchema, ExamSchema
from django.db.models import Q

router = Router()

@router.post("/", response=ExamSchema)
def create_exam(request, data: ExamCreateSchema):
    if not request.user.is_authenticated:
        return {"detail":"Authentication required"}, 401
    
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

@router.get("/{exam_id}/", response=ExamSchema)
def get_exam(request, exam_id: int):
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        return {"detail":"Exam not found"}, 404
    return ExamSchema.from_orm(exam)

@router.put("/{exam_id}/", response=ExamSchema)
def update_exam(request, exam_id:int, data: ExamCreateSchema):
    if not request.user.is_authenticated:
        return {"detail": "Authentication required"}, 401
    
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        return {"detail":"Exam not found"}, 404

    exam.name = data.name
    exam.save()
    return ExamSchema.from_orm(exam)    

@router.patch("/{exam_id}/", response=ExamSchema)
def partial_update_exam(request, exam_id: int, data: ExamCreateSchema):
    if not request.user.is_authenticated:
        return {"detail":"Authentication required"}, 401
    
    try:
        exam= ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        return {"detail":"Exam not found"}, 404

    if data.name is not None:
        exam.name = data.name
    exam.save()
    return ExamSchema.from_orm(exam)

@router.delete("/{exam_id}/", response={204: None})
def delete_exam(request, exam_id:int):
    if not request.user.is_authenticated:
        return {"detail":"Authentication required"}, 401
    
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        return {"detail": "Exam not found"}, 404

    exam.delete()
    return 204, None    