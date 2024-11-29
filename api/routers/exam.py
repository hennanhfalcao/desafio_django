from ninja import Router
from django.shortcuts import get_object_or_404
from api.models import ModelExam, ModelParticipation
from api.schemas import ExamSchema, ExamCreateSchema, ExamUpdateSchema, ErrorSchema, ParticipationSchema, ParticipationCreateSchema
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset
from ninja.errors import HttpError
from django.db.models import Q
from django.contrib.auth.models import User

router = Router(tags=["Exams"])

@router.post("/", response={201: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_exam(request, payload: ExamCreateSchema):
    """Cria uma prova
    Apenas administradores podem criar provas."""
    is_authenticated(request)
    is_admin(request)

    exam = ModelExam.objects.create(name=payload.name, created_by=request.user)
    return 201, ExamSchema.model_validate(exam)

@router.get("/", response={200: list[ExamSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_exams(request, query: str = None, order_by: str = "-name", page: int = 1, page_size: int = 10):
    """Lista todas as provas com busca, ordenação e paginação opcionais."""
    is_authenticated(request)
    is_admin(request)

    try:    
        exams = ModelExam.objects.all()
    except ModelExam.DoesNotExist:
        raise HttpError(404, "Não foram encontradas provas")
        
    if query:
        exams = exams.filter(Q(name__icontains=query))

    exams = order_queryset(exams, order_by)

    exams = paginate_queryset(exams, page, page_size)

    return [ExamSchema.model_validate(exam) for exam in exams]


@router.get("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_exam_details(request, exam_id: int):
    """Recupera detalhes da prova por meio do ID.
    Participantes podem recuperar informações das provas em que estão inscritos"""
    is_authenticated(request)

    exam = get_object_or_404(ModelExam, id=exam_id)

    if not request.user.profile.is_admin and not ModelParticipation.objects.filter(user=request.user, exam__id=exam_id).exists():   
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

    return ExamSchema.model_validate(exam)

@router.put("/put/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def update_exam(request, exam_id: int, payload: ExamUpdateSchema):
    """Atualiza completamente uma prova por meio do seu ID"""
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    exam.name = payload.name
    exam.save()

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

    """Cria uma nova participação para um usuário em uma prova pelo ID do usuário e o ID da prova."""

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

    return 200, ParticipationSchema.model_validate(participation)


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