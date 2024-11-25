from typing import List
from ninja import Router
from api.models import ModelQuestion, ModelExam
from api.schemas import QuestionSchema, QuestionCreateSchema
from django.db.models import Q

router = Router()

@router.post("/", response=QuestionSchema)
def create_question(request, data: QuestionCreateSchema):
    if not request.user.is_authenticated:
        return {"detail":"Authentication required"}, 401
    
    try:
        exam = ModelExam.objects.get(id=data.exam_id)
    except ModelExam.DoesNotExist:
        return {"detail":"Exam not found"}, 404
    question = ModelQuestion.objects.create(exam=exam, text=data.text)
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

@router.get("/{question_id}/", response=QuestionSchema)
def get_question(request, question_id:int):
    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        return {"detail":"Question not found"}, 404
    return QuestionSchema.from_orm(question)


@router.put("/{question_id}/", response=QuestionSchema)
def update_question(request, question_id: int, data: QuestionCreateSchema):
    if not request.user.is_authenticated:
        return {"detail":"Authentication required"}, 401
    
    try: 
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        return {"detail":"Question not found"},  404
    
    question.text = data.text
    if data.exam_id:
        try:
            exam=ModelExam.objects.get(id=data.exam_id)
            question.exam=exam
        except ModelExam.DoesNotExist:
            return {"detail":"Exam not found"}, 404
    question.save()
    return QuestionSchema.from_orm(question)

@router.patch("/{question_id}/", response=QuestionSchema)
def partial_update_question(request, question_id:int, data: QuestionCreateSchema):
    if not request.user.is_authenticated:
        return {"detail":"Authentication required"}, 401
    
    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        return {"detail":"Question not found"}, 404
    
    if data.text is not None:
        question.text = data.text
    if data.exam_id is not None:
        try:
            exam = ModelExam.objects.get(id=data.exam_id)
            question.exam = exam
        except ModelExam.DoesNotExist:
            return {"detail":"Exam not found"}, 404
    question.save()
    return QuestionSchema.from_orm(question)     


@router.delete("/{question_id}/", response={204:None})
def delete_question(request, question_id:int):
    if not request.user.is_authenticated:
        return {"detail":"Authentication required"}, 401
    
    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        return {"detail":"Question not found"}, 404
    
    question.delete()
    return 204, None