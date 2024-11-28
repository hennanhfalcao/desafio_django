from typing import List, Optional
from ninja import Router
from api.models import ModelChoice, ModelQuestion
from api.schemas import ChoicesSchema, ChoicesCreateSchema, ChoicesUpdateSchema, ErrorSchema
from api.utils import is_authenticated, is_admin, paginate_queryset, order_queryset
from django.db.models import Q
from ninja.errors import HttpError

router = Router(tags=["Choices"])


@router.post("/", response={200: ChoicesSchema, 400: ErrorSchema, 401: ErrorSchema, 403: ErrorSchema})
def create_choice(request, payload: ChoicesCreateSchema):
    is_authenticated(request)
    is_admin(request)

    try:
        question = ModelQuestion.objects.get(id=payload.question_id)
    except ModelQuestion.DoesNotExist:
        raise HttpError(404,"Question not found")


    if question.choices.count() >= 4:
        raise HttpError(400,"A question must have exactly 4 choices.")

    # Criar a alternativa
    choice = ModelChoice.objects.create(
        question=question,
        text=payload.text,
        is_correct=payload.is_correct
    )
    return ChoicesSchema.from_orm(choice)


@router.get("/", response={200: List[ChoicesSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_choices(
    request, 
    query: Optional[str] = None, 
    question_id: Optional[int] = None, 
    order_by: str = "id", 
    page: int = 1, 
    page_size: int = 10
):
    is_authenticated(request)

    choices = ModelChoice.objects.all()

    if question_id:
        choices = choices.filter(question_id=question_id)

    if query:
        choices = choices.filter(Q(text__icontains=query))

    choices = order_queryset(choices, order_by)
    choices = paginate_queryset(choices, page, page_size)

    return [ChoicesSchema.from_orm(choice) for choice in choices]


@router.get("/{choice_id}/", response={200: ChoicesSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_choice(request, choice_id: int):
    is_authenticated(request)

    try:
        choice = ModelChoice.objects.get(id=choice_id)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    return ChoicesSchema.from_orm(choice)


@router.put("/{choice_id}/", response={200: ChoicesSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def update_choice(request, choice_id: int, payload: ChoicesUpdateSchema):
    is_authenticated(request)
    is_admin(request)

    try:
        choice = ModelChoice.objects.get(id=choice_id)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(choice, attr, value)
    choice.save()

    return ChoicesSchema.from_orm(choice)


# Atualização parcial de uma alternativa
@router.patch("/{choice_id}/", response={200: ChoicesSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def partial_update_choice(request, choice_id: int, payload: ChoicesUpdateSchema):
    return update_choice(request, choice_id, payload)


# Exclusão de uma alternativa
@router.delete("/{choice_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_choice(request, choice_id: int):
    is_authenticated(request)
    is_admin(request)

    try:
        choice = ModelChoice.objects.get(id=choice_id)
    except ModelChoice.DoesNotExist:
        raise HttpError(404, "Choice not found")

    choice.delete()
    return 204, None