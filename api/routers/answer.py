from ninja import Router
from django.shortcuts import get_object_or_404
from api.models import ModelChoice, ModelQuestion, ModelAnswer, ModelParticipation
from api.schemas import ExamSchema, ExamCreateSchema, ExamUpdateSchema, ErrorSchema, ParticipationSchema, ParticipationCreateSchema, ParticipationUpdateSchema, AnswerSchema, AnswerCreateSchema, AnswerUpdateSchema
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset
from ninja.errors import HttpError
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

router = Router(tags=["Answers"])


@router.post("/", response={201: AnswerSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def create_answer(request, payload: AnswerCreateSchema):

    """Cria uma nova resposta para um usuário em uma prova pelo ID do usuário e o ID da prova."""

    is_authenticated(request)

    if request.user.is_admin:
        raise HttpError(403, "Apenas participantes podem responder questões.")
    
    participation = get_object_or_404(ModelParticipation, id=payload.participation_id, user=request.user)

    question = get_object_or_404(ModelQuestion, id=payload.question_id)

    if not question.exams.filter(id=participation.exam.id).exists():
        raise HttpError(403, "Apenas participantes podem responder questões da prova.")

    choice = get_object_or_404(ModelChoice, id=payload.choice_id, question=question)


    answer = ModelAnswer.objects.create(
        participation=participation,
        question=question,
        choice = choice
    )

    return 201, AnswerSchema.model_validate(answer)

@router.patch("/patch/{answer_id}/", response={200: AnswerSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def update_answer(request, answer_id: int, payload: AnswerUpdateSchema):
    is_authenticated(request)

    answer = get_object_or_404(ModelAnswer, id=answer_id)

    if answer.participation.user != request.user:
        raise HttpError(403, "Apenas o autor da resposta pode atualizá-la.")

    if payload.choice_id:
        choice = get_object_or_404(ModelChoice, id=payload.choice_id, question=answer.question)
        answer.choice = choice

    answer.save()
    return 200, AnswerSchema.model_validate(answer)

@router.get("/", response={200: dict, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def list_answers(request, participation_id: int):
    """Lista todas as respostas de um participante em uma prova.
    Apenas participantes podem listar suas proprias respostas."""
    is_authenticated(request)

    participation = get_object_or_404(ModelParticipation, id=participation_id, user=request.user)

    answer = ModelAnswer.objects.filter(participation=participation)

    return {"results": [AnswerSchema.model_validate(answer) for answer in answer]}

@router.get("/get/{answer_id}/", response={200: AnswerSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def get_answer_details(request, answer_id: int):

    """Recupera detalhes de uma resposta por meio do ID."""
    is_authenticated(request)

    answer = get_object_or_404(ModelAnswer, id=answer_id)

    if answer.participation.user != request.user:
        raise HttpError(403, "Apenas o autor da resposta pode obter seus detalhes.")

    return AnswerSchema.model_validate(answer)

@router.delete("/{answer_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def delete_answer(request, answer_id: int):
    """Deleta uma resposta por meio do ID.
    Apenas o autor da resposta pode deletá-la."""
    is_authenticated(request)

    answer = get_object_or_404(ModelAnswer, id=answer_id)

    if answer.participation.user != request.user:
        raise HttpError(403, "Apenas o autor da resposta pode deletá-la.")

    answer.delete()

    return 204, None