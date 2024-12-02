from ninja import Router
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from api.models import ModelExam, ModelParticipation
from api.schemas import ExamSchema, ExamCreateSchema, ExamUpdateSchema, ErrorSchema, ParticipationSchema, ParticipationCreateSchema, ParticipationUpdateSchema
from api.tasks import calculate_score
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset, clear_list_exams_cache, add_cache_key
from ninja.errors import HttpError
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()

router = Router(tags=["Exams"])

@router.post("/", response={201: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_exam(request, payload: ExamCreateSchema):
    """Cria uma prova
    Apenas administradores podem criar provas.
    Crie provas apenas com o nome e, após inseridas as questões no banco de dados. faça o link entre as entidades pela rota /api/questions/{question_id}/link-exam/{exam_id}/ 
    """
    is_authenticated(request)
    is_admin(request)

    exam = ModelExam.objects.create(name=payload.name, created_by=request.user)
    clear_list_exams_cache()
    return 201, ExamSchema.model_validate(exam)

@router.get("/", response={200: list[ExamSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_exams(request, query: str = None, order_by: str = "-name", page: int = 1, page_size: int = 10):
    """Lista todas as provas com busca, ordenação e paginação opcionais.
    É possível ordená-las por meio do campo created_at por meio da rota: /api/exams/?order_by=-name
    A páginação é feita por meio da rota: /api/exams/?page=2&page_size=10, em que os parâmetros page e page_size podem ser alterados.
    A busca por string é feita pelo campo text e pode ser testada acessando a rota: /api/exams/?query="""
    is_authenticated(request)
    is_admin(request)

    cache_key = f"list_exams:{query}:{order_by}:{page}:{page_size}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"Cache hit for key: {cache_key}")
        return cached_data

    try:    
        exams = ModelExam.objects.all()
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Não foram encontradas provas")
        
    if query:
        exams = exams.filter(Q(name__icontains=query))

    exams = order_queryset(exams, order_by)

    exams = paginate_queryset(exams, page, page_size)

    results = [ExamSchema.model_validate(exam) for exam in exams]
    cache.set(cache_key, results, timeout=300)
    add_cache_key(cache_key)
    return results


@router.get("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_exam_details(request, exam_id: int):
    """Recupera detalhes da prova por meio do ID.
    Participantes podem recuperar informações das provas em que estão inscritos"""
    is_authenticated(request)

    exam = get_object_or_404(ModelExam, id=exam_id)

    if not request.user.is_admin and not ModelParticipation.objects.filter(user=request.user, exam__id=exam_id).exists():   
        raise HttpError(403, "Você não tem permissão para acessar os detalhes desta prova")
    
    return ExamSchema.model_validate(exam)

@router.patch("/patch/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def partial_update_exam(request, exam_id: int, payload: ExamUpdateSchema):
    """Atualiza parcialmente uma prova por meio do seu ID"""
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(exam, attr, value)
    exam.save()
    clear_list_exams_cache()
    return ExamSchema.model_validate(exam)

@router.put("/put/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def update_exam(request, exam_id: int, payload: ExamUpdateSchema):
    """Atualiza completamente uma prova por meio do seu ID"""
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    exam.name = payload.name
    exam.save()
    clear_list_exams_cache()
    return ExamSchema.model_validate(exam)

@router.delete("/{exam_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_exam(request, exam_id: int):
    """Deleta uma prova pelo ID.
    Apenas administradores podem deletar provas."""
    is_authenticated(request)
    is_admin(request)

    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Prova não encontrada")

    exam.delete()
    clear_list_exams_cache()
    return 204, None

@router.get("/{exam_id}/participants/", response={200: list[ParticipationSchema], 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def list_participants(request, exam_id: int):
    """Lista os participantes de uma prova por meio do ID
    Apenas administradores podem listar os participantes de uma prova."""
    is_authenticated(request)
    is_admin(request)

    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Prova não encontrada")

    return [ParticipationSchema.model_validate(participation) for participation in ModelParticipation.objects.filter(exam=exam)]

@router.post("/{exam_id}/participants/", response={201: ParticipationSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def create_participation(request, exam_id: int, payload: ParticipationCreateSchema):

    """Cria uma nova participação para um usuário em uma prova pelo ID do usuário e o ID da prova
    Após criada a participação, de posse do ID da participação é possível responder à prova enviando uma solicitação POST para a rota /api/answer/.
    """

    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=payload.user_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuário nao encontrado")

    try:
        exam = ModelExam.objects.get(id=payload.exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Prova nao encontrada")

    if ModelParticipation.objects.filter(user=user, exam=exam).exists():
        raise HttpError(422, "Usuário ja inscrito na prova")

    participation = ModelParticipation.objects.create(user=user, exam=exam)

    return 201, ParticipationSchema.model_validate(participation)


@router.delete("/{exam_id}/participants/{user_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_participation(request, exam_id: int, user_id: int):
    """Deleta uma participação de um usuário em uma prova pelo ID do usuário e o ID da prova.
    Apenas administradores podem deletar participações."""
    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuário nao encontrado")

    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Prova nao encontrada")

    if not ModelParticipation.objects.filter(user=user, exam=exam).exists():
        raise HttpError(404, "Participação nao encontrada")

    ModelParticipation.objects.filter(user=user, exam=exam).delete()

    return 204, None

@router.get("/{exam_id}/participants/{user_id}/", response={200: ParticipationSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})    
def get_participation_details(request, exam_id: int, user_id: int):
    """Obtem detalhes de uma participação de um usuário em uma prova pelo ID do usuário e o ID da prova.
    Apenas administradores podem obter detalhes de participações."""
    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuário nao encontrado")

    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Prova nao encontrada")

    if not ModelParticipation.objects.filter(user=user, exam=exam).exists():
        raise HttpError(404, "Participação nao encontrada")

    return ParticipationSchema.model_validate(ModelParticipation.objects.get(user=user, exam=exam))

@router.patch("/{exam_id}/participants/{user_id}/", response={200: ParticipationSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def update_participation(request, exam_id: int, user_id: int, payload: ParticipationUpdateSchema):
    """Atualiza uma participação de um usuário em uma prova pelo ID do usuário e o ID da prova.
    Apenas administradores podem atualizar participações."""

    is_authenticated(request)
    is_admin(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "Usuário nao encontrado")

    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Prova nao encontrada")

    if not ModelParticipation.objects.filter(user=user, exam=exam).exists():
        raise HttpError(404, "Participação nao encontrada")

    participation = ModelParticipation.objects.get(user=user, exam=exam)

    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(participation, attr, value)

    participation.save()

    return 200, ParticipationSchema.model_validate(participation)

@router.post("{exam_id}/finish/", response={200:dict, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def finish_exam(request, exam_id: int):
    """Finaliza uma prova para um participante e inicia o cálculo da pontuação.
    Portanto, para testar essa funcionalidade, crie uma participação, responda à prova e, aí sim, envie uma solicitação post para esta rota para que a prova seja finalizada e o celery inicie o cálculo da pontuação.
    Além dio mais, o ranking é atualizado conforme as participações nas provas são finalizadas.
    Para obter o ranking por prova acesse: GET /api/ranking/{exam_id}/ranking/"""

    is_authenticated(request)
    
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Prova nao encontrada")

    try:
        participation = ModelParticipation.objects.get(user=request.user, exam__id=exam_id)
    except ModelParticipation.DoesNotExist:
        raise HttpError(404, "Participação nao encontrada")

    
    if participation.finished_at:
        raise HttpError(403, "Prova ja finalizada")
    
    calculate_score.delay(participation.id)

    return 200, {"detail":"Cálculo da pontuação iniciado"}

@router.get("/{exam_id}/progress/", response={200:dict, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def check_progress(request, exam_id: int):
    """Verifica o progresso da correção da prova.
    Se a correção tiver sido finalizada, retornará o score para o participante"""
    is_authenticated(request)
    try:
        participation = ModelParticipation.objects.get(user=request.user, exam_id=exam_id)
    except ModelParticipation.DoesNotExist:
        raise HttpError(404, "Participação não encontrada")
    
    if participation.finished_at:
        return {"status": "completed", "score": participation.score}
    else:
        return {"status": "in_progress"}

