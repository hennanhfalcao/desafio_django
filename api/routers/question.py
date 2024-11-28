from typing import List, Optional
from ninja import Router
from api.models import ModelExamQuestion, ModelQuestion, ModelExam, ModelChoice
from api.schemas import (
    QuestionSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    ErrorSchema,
    ChoicesSchema,
    ChoicesCreateSchema,
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
    choices = list(ModelChoice.objects.filter(question=question))
    question_data = {
        "id": question.id,
        "text": question.text,
        "created_at": question.created_at,
        "exams": exam_ids,
        "choices": [
            {"id": choice.id, "question_id": question.id, "text": choice.text, "is_correct": choice.is_correct}
            for choice in choices
        ],
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
        choices = list(ModelChoice.objects.filter(question=question))
        question_data = {
            "id": question.id,
            "text": question.text,
            "created_at": question.created_at,
            "exams": exam_ids,
            "choices": [
                {"id": choice.id, "question_id": question.id, "text": choice.text, "is_correct": choice.is_correct}
                for choice in choices
            ],
        }
        result.append(question_data)

    return result


@router.get("/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_question(request, question_id: int):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    exam_ids = list(ModelExamQuestion.objects.filter(question=question).values_list("exam_id", flat=True))
    choices = list(ModelChoice.objects.filter(question=question))
    question_data = {
        "id": question.id,
        "text": question.text,
        "created_at": question.created_at,
        "exams": exam_ids,
        "choices": [
            {"id": choice.id, "question_id": question.id, "text": choice.text, "is_correct": choice.is_correct}
            for choice in choices
        ],
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

    exam_ids = list(ModelExamQuestion.objects.filter(question=question).values_list("exam_id", flat=True))
    choices = list(ModelChoice.objects.filter(question=question))
    question_data = {
        "id": question.id,
        "text": question.text,
        "created_at": question.created_at,
        "exams": exam_ids,
        "choices": [
            {"id": choice.id, "question_id": question.id, "text": choice.text, "is_correct": choice.is_correct}
            for choice in choices
        ],
    }

    return QuestionSchema(**question_data)


@router.delete("/{question_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_question(request, question_id: int):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    question.delete()
    return 204, None


""" Gerenciamento de Alternativas de uma Questão """

@router.get("/{question_id}/choices/", response={200: List[ChoicesSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_choices(request, question_id: int):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    choices = ModelChoice.objects.filter(question=question)
    return [
        {"id": choice.id, "question_id": question.id, "text": choice.text, "is_correct": choice.is_correct}
        for choice in choices
    ]


@router.post("/{question_id}/choices/", response={200: ChoicesSchema, 400: ErrorSchema, 401: ErrorSchema, 403: ErrorSchema})
def add_choice(request, question_id: int, payload: ChoicesCreateSchema):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    if ModelChoice.objects.filter(question=question).count() >= 4:
        raise HttpError(400, "A question can have at most 4 choices")

    payload_data = payload.dict()
    payload_data["question_id"] = question_id

    choice = ModelChoice.objects.create(
        question=question,
        text=payload.text,
        is_correct=payload.is_correct,
    )
    choice_data = {
        "id": choice.id,
        "question_id": question.id,
        "text": choice.text,
        "is_correct": choice.is_correct,
    }
    return ChoicesSchema(**choice_data)


@router.delete("/{question_id}/choices/{choice_id}/", response={204: None, 400: ErrorSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def remove_choice(request, question_id: int, choice_id: int):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    try:
        choice = ModelChoice.objects.get(id=choice_id, question=question)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    if ModelChoice.objects.filter(question=question).count() <= 2:
        raise HttpError(400, "A question must have at least 2 choices")

    choice.delete()
    return 204, None