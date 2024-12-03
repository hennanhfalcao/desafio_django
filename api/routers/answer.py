from ninja import Router
from django.shortcuts import get_object_or_404
from api.models import ModelChoice, ModelQuestion, ModelAnswer, ModelParticipation
from api.schemas import ErrorSchema, AnswerSchema, AnswerCreateSchema, AnswerUpdateSchema
from api.utils import is_authenticated, order_queryset, paginate_queryset, clear_list_answers_cache, add_answer_cache_key
from ninja.errors import HttpError
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

router = Router(tags=["Answers"])


@router.post("/", response={201: AnswerSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def create_answer(request, payload: AnswerCreateSchema):

    """Cria uma nova resposta para um usuário em uma prova pelo ID do usuário e o ID da prova.
    Lembre-se que para responder, quem tem que estar autenticado é o usuário que irá responder a questão."""

    is_authenticated(request)
    
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
    clear_list_answers_cache()
    return 201, AnswerSchema.model_validate(answer)

@router.patch("/{answer_id}/", response={200: AnswerSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def update_answer(request, answer_id: int, payload: AnswerUpdateSchema):
    """Atualiza uma resposta.
    Apenas o autor da resposta pode atualizá-la."""
    
    is_authenticated(request)

    answer = get_object_or_404(ModelAnswer, id=answer_id)

    if answer.participation.user != request.user:
        raise HttpError(403, "Apenas o autor da resposta pode atualizá-la.")

    if payload.choice_id:
        choice = get_object_or_404(ModelChoice, id=payload.choice_id, question=answer.question)
        answer.choice = choice

    answer.save()
    clear_list_answers_cache()
    return 200, AnswerSchema.model_validate(answer)

@router.get("/participants/{participation_id}/", response={200: list[AnswerSchema], 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def list_answers(
    request,
    participation_id: int,
    query: str = None,
    order_by: str = "-id",
    page: int = 1,
    page_size: int = 10,
):
    """
    Lista todas as respostas com busca, ordenação e paginação opcionais.
    É possível ordená-las por meio do campo "id" por meio da rota: /api/answers/participants/{participation_id}/?order_by=-id
    A páginação é feita por meio da rota: /api/answers/participants/{participation_id}/?page=<int>&page_size=<int>, em que os parâmetros page e page_size podem ser alterados.
    A busca por string é feita pelo campo text e pode ser testada acessando a rota: /api/answers/participants/{participation_id}/?query=
    """
    is_authenticated(request)

    cache_key = f"answers-{participation_id}-{request.user.id}-{query}-{order_by}-{page}-{page_size}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data 

    participation = get_object_or_404(ModelParticipation, id=participation_id, user=request.user)

    answers = ModelAnswer.objects.filter(participation=participation)

    if query:
        answers = answers.filter(Q(question__text__icontains=query) | Q(choice__text__icontains=query))

    answers = order_queryset(answers, order_by)
    answers = paginate_queryset(answers, page, page_size)

    results = [AnswerSchema.model_validate(answer) for answer in answers]

    cache.set(cache_key, results, timeout=300)
    add_answer_cache_key(cache_key)

    return results

@router.get("/{answer_id}/", response={200: AnswerSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def get_answer_details(request, answer_id: int):

    """Recupera detalhes de uma resposta por meio do ID.
    Lembre-se de estar autenticado com o participante"""
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
    clear_list_answers_cache()
    return 204, None