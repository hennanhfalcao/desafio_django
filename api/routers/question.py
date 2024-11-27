from typing import List, Optional
from ninja import Router, Schema
from api.models import ModelQuestion, ModelExam, ModelParticipation
from api.schemas import QuestionSchema, QuestionCreateSchema, ErrorSchema, QuestionUpdateSchema
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset
from django.db.models import Q
from ninja.errors import HttpError
import random

router = Router(tags=["Questions"])

@router.post("/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema})
def create_question(
        request, 
        payload: QuestionCreateSchema
    ):

    """
    Criação de uma nova questão sem vincular diretamente a uma prova.
    Apenas administradores têm permissão.
    """

    is_authenticated(request)
    is_admin(request)

    question = ModelQuestion.objects.create(text=payload.text)
    return QuestionSchema.from_orm(question)

@router.post("/exams/{exam_id}/questions/link-random/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def link_random_question(
        request, 
        exam_id: int
    ):

    """
    Vincula uma questão aleatória a uma prova específica.
    Apenas administradores têm permissão.
    """
    
    is_authenticated(request)
    is_admin(request)
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, {"detail": "Exam not found"})
    
    available_questions = ModelQuestion.objects.exclude(exams=exam)

    if not available_questions.exists():
        raise HttpError(404, {"detail": "No available questions to link"})

    question = random.choice(available_questions)
    question.exams.add(exam)

    return QuestionSchema.from_orm(question)

@router.post("exams/{exam_id}/questions/link-specific/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def link_specific_question(
        request, 
        exam_id: int, 
        question_id: int
    ):

    """
    Vincula uma questão específica a uma prova.
    Apenas administradores têm permissão.
    """

    is_authenticated(request)
    is_admin(request)
    try:
        exam = ModelExam.objects.get(id=exam_id)
        question = ModelQuestion.objects.get(id=question_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, {"detail": "Exam not found"})
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, {"detail": "Question not found"})

    if exam in question.exams.all():
        raise HttpError(400, {"detail": "Question already linked to this exam"})

    question.exams.add(exam)

    return QuestionSchema.from_orm(question)

@router.get("/", response={200: List[QuestionSchema], 401: ErrorSchema})
def list_all_questions(
        request, 
        query: str = None, 
        order_by: str = "created_at", 
        page: int = 1, 
        page_size: int = 10
    ):

    """
    Lista todas as questões cadastradas no banco.
    Apenas administradores podem acessar essa lista completa.
    """

    is_authenticated(request)
    is_admin(request)
    
    questions = ModelQuestion.objects.all()
    if query:
        questions = questions.filter(Q(text__icontains=query))

    questions = order_queryset(questions, order_by)
    questions = paginate_queryset(questions, page, page_size)

    return [QuestionSchema.from_orm(question) for question in questions]    


@router.post("/exams/{exam_id}/questions/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def create_question_by_exam(request, exam_id: int, payload: QuestionCreateSchema):
    """
    Criação de uma nova questão vinculada diretamente a uma prova.
    Apenas Administradores tem permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, {"detail": "Exam not found"})
    
    question = ModelQuestion.objects.create(text=payload.text)
    question.exams.add(exam)
    return QuestionSchema.from_orm(question)

@router.get("/exams/{exam_id}/questions/", response={200: List[QuestionSchema], 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def list_questions_by_exam(
    request, 
    exam_id: int, 
    query: str = None, 
    order_by: str = "created_at", 
    page: int = 1, page_size: 
    int = 10
    ):

    """
    Lista perguntas de uma prova específica com suporte a busca, ordenação e paginação.
    """

    is_authenticated(request)

    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        return HttpError(404, {"detail": "Exam not found"})

    if not request.user.profile.is_admin:
        if not ModelParticipation.objects.filter(exam=exam, user=request.user).exists():
            return HttpError(403, {"detail": "Permission denied"})

    questions = ModelQuestion.objects.filter(exams=exam)

    if query:
        questions = questions.filter(Q(text__icontains=query))

    questions = order_queryset(questions, order_by)
    questions = paginate_queryset(questions, page, page_size)

    return [QuestionSchema.from_orm(question) for question in questions]

@router.get("/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_question(request, question_id:int):
    """
    Resgata detalhes de uma questão específica.
    Apenas administradores podem acessar essa informação.
    """
    is_authenticated(request)
    is_admin(request)
    
    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, {"detail": "Question not found"})
    
    return QuestionSchema.from_orm(question)


@router.put("/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_question(request, question_id:int, payload: QuestionUpdateSchema):
    """Atualiza completamente uma questão"
    Apenas administradores podem acessar essa informação."""
    is_authenticated(request)
    is_admin(request)
    
    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, {"detail": "Question not found"})
    
    question.text = payload.text
    question.save()
    return QuestionSchema.from_orm(question)

@router.put("/exams/{exam_id}/questions/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_question_by_exam(request, exam_id: int, question_id: int, payload: QuestionUpdateSchema):
    """
    Atualiza uma questão vinculada diretamente a uma prova.
    Apenas Administradores tem permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        exam = ModelExam.objects.get(id=exam_id)
        question = ModelQuestion.objects.get(id=question_id, exams=exam)
    except ModelExam.DoesNotExist:
        raise HttpError(404, {"detail": "Exam not found"})
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, {"detail": "Question not found"})
    
    if payload.text:
        question.text = payload.text
    question.save()
    return QuestionSchema.from_orm(question)


@router.delete("/{question_id}/", response={204:None})
def delete_question(request, question_id:int):
    """
    Apaga uma questão pelo seu ID.
    Apenas administradores podem acessar essa informação.
    """
    
    is_authenticated(request)
    is_admin(request)
    
    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, {"detail": "Question not found"})
    
    question.delete()
    return 204, None

@router.delete("/exams/{exam_id}/questions/{question_id}/", response={204:None})
def unlink_question(request, exam_id: int, question_id: int):
    """
    Apaga uma questão vinculada diretamente a uma prova.
    Apenas Administradores tem permissão."""
    
    is_authenticated(request)
    is_admin(request)

    try:
        exam = ModelExam.objects.get(id=exam_id)
        question = ModelQuestion.objects.get(id=question_id, exams=exam)
    except ModelExam.DoesNotExist:
        raise HttpError(404, {"detail": "Exam not found"})
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, {"detail": "Question not linked to this exam"})
    
    question.exams.remove(exam)
    return 204, None