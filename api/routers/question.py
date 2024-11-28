from typing import List, Optional
from ninja import Router
from api.models import ModelExamQuestion, ModelQuestion, ModelExam
from api.schemas import (
    QuestionSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    ErrorSchema,
)
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset
from ninja.errors import HttpError
from django.db.models import Q

router = Router(tags=["Questions"])

""" Gerenciamento Geral de Questões """

@router.post("/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema})
def create_question(request, payload: QuestionCreateSchema):
    is_authenticated(request)
    is_admin(request)

    question = ModelQuestion.objects.create(text=payload.text)

    if payload.exams:
        for exam_id in payload.exams:
            exam = ModelExam.objects.get(id=exam_id)
            ModelExamQuestion.objects.create(exam=exam, question=question)

    exam_ids = list(ModelExamQuestion.objects.filter(question=question).values_list("exam_id", flat=True))
    question_data = {
        "id": question.id,
        "text": question.text,
        "created_at": question.created_at,
        "exams": exam_ids,
    }

    return QuestionSchema(**question_data)

@router.get("/", response={200: List[QuestionSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_all_questions(
    request,
    query: Optional[str] = None,
    order_by: str = "created_at",
    page: int = 1,
    page_size: int = 10,
):
    is_authenticated(request)
    is_admin(request)

    questions = ModelQuestion.objects.all()
    if query:
        questions = questions.filter(Q(text__icontains=query))

    questions = order_queryset(questions, order_by)
    questions = paginate_queryset(questions, page, page_size)

    result = []
    for question in questions:
        exam_ids = list(ModelExamQuestion.objects.filter(question=question).values_list("exam_id", flat=True))
        question_data = {
            "id": question.id,
            "text": question.text,
            "created_at": question.created_at,
            "exams": exam_ids,
        }
        result.append(QuestionSchema(**question_data))

    return result


@router.get("/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_question(request, question_id: int):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    # Busca os IDs dos exames relacionados
    exam_ids = list(ModelExamQuestion.objects.filter(question=question).values_list("exam_id", flat=True))

    # Monta os dados manualmente
    question_data = {
        "id": question.id,
        "text": question.text,
        "created_at": question.created_at,
        "exams": exam_ids,
    }

    return QuestionSchema(**question_data)

@router.put("/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_question(request, question_id: int, payload: QuestionUpdateSchema):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    if payload.text:
        question.text = payload.text
        question.save()

    if payload.exams is not None:
        ModelExamQuestion.objects.filter(question=question).delete()
        for exam_id in payload.exams:
            exam = ModelExam.objects.get(id=exam_id)
            ModelExamQuestion.objects.create(exam=exam, question=question)

    # Construir os dados manualmente
    exam_ids = list(ModelExamQuestion.objects.filter(question=question).values_list("exam_id", flat=True))
    question_data = {
        "id": question.id,
        "text": question.text,
        "created_at": question.created_at,
        "exams": exam_ids,
    }

    return QuestionSchema(**question_data)

@router.delete("/{question_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_question(request, question_id: int):
    """
    Apaga uma questão pelo seu ID.
    Apenas administradores têm permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    question.delete()
    return 204, None