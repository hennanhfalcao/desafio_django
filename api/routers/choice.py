from typing import List
from ninja import Router
from api.models import ModelChoice, ModelQuestion
from api.schemas import (
    ChoicesSchema,
    ChoicesCreateSchema,
    ChoicesUpdateSchema,
    ErrorSchema,
)
from api.utils import is_authenticated, is_admin
from ninja.errors import HttpError

router = Router(tags=["Choices"])


@router.post("/", response={200: ChoicesSchema, 401: ErrorSchema, 403: ErrorSchema})
def create_choice(request, payload: ChoicesCreateSchema):
    """
    Cria uma nova alternativa para uma questão.
    Apenas administradores têm permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=payload.question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404, "Question not found")

    choice = ModelChoice.objects.create(
        question=question, text=payload.text, is_correct=payload.is_correct
    )

    choice_data = {
        "id": choice.id,
        "question_id": choice.question.id,
        "text": choice.text,
        "is_correct": choice.is_correct,
    }

    return ChoicesSchema(**choice_data)


@router.get("/{choice_id}/", response={200: ChoicesSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_choice(request, choice_id: int):
    """
    Recupera uma alternativa específica pelo seu ID.
    Apenas administradores têm permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        choice = ModelChoice.objects.get(id=choice_id)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    choice_data = {
        "id": choice.id,
        "question_id": choice.question.id,
        "text": choice.text,
        "is_correct": choice.is_correct,
    }

    return ChoicesSchema(**choice_data)


@router.put("/{choice_id}/", response={200: ChoicesSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_choice(request, choice_id: int, payload: ChoicesUpdateSchema):
    """
    Atualiza completamente uma alternativa pelo seu ID.
    Apenas administradores têm permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        choice = ModelChoice.objects.get(id=choice_id)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    if payload.text is not None:
        choice.text = payload.text
    if payload.is_correct is not None:
        choice.is_correct = payload.is_correct

    choice.save()

    choice_data = {
        "id": choice.id,
        "question_id": choice.question.id,
        "text": choice.text,
        "is_correct": choice.is_correct,
    }

    return ChoicesSchema(**choice_data)


@router.patch("/{choice_id}/", response={200: ChoicesSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def partial_update_choice(request, choice_id: int, payload: ChoicesUpdateSchema):
    """
    Atualiza parcialmente uma alternativa pelo seu ID.
    Apenas administradores têm permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        choice = ModelChoice.objects.get(id=choice_id)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(choice, attr, value)

    choice.save()

    choice_data = {
        "id": choice.id,
        "question_id": choice.question.id,
        "text": choice.text,
        "is_correct": choice.is_correct,
    }

    return ChoicesSchema(**choice_data)


@router.delete("/{choice_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_choice(request, choice_id: int):
    """
    Deleta uma alternativa pelo seu ID.
    Apenas administradores têm permissão.
    """
    is_authenticated(request)
    is_admin(request)

    try:
        choice = ModelChoice.objects.get(id=choice_id)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    choice.delete()
    return 204, None