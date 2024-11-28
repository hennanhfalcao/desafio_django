from ninja import Router
from django.db.models import Q
from api.models import (
    ModelExam,
    ModelExamParticipant,
    ModelExamQuestion,
    ModelQuestion,
    User,
)
from api.schemas import (
    ExamSchema,
    ExamCreateSchema,
    ExamUpdateSchema,
    ExamParticipantSchema,
    ExamParticipantCreateSchema,
    ExamQuestionSchema,
    ExamQuestionCreateSchema,
    ErrorSchema,
)
from api.utils import is_authenticated, is_admin, paginate_queryset, order_queryset
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

router = Router(tags=["Exams"])


@router.post("/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_exam(request, payload: ExamCreateSchema):
    """Cria uma nova prova (Apenas administradores)."""
    is_authenticated(request)
    is_admin(request)
    exam = ModelExam.objects.create(name=payload.name, created_by=request.user)
    return ExamSchema.from_orm(exam)


@router.get("/", response={200: list[ExamSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_exams(request, query: str = None, order_by: str = "id", page: int = 1, page_size: int = 10):
    """
    Lista as provas. 
    - Administradores veem todas as provas.
    - Participantes veem apenas as provas em que estão inscritos.
    """
    is_authenticated(request)

    if request.user.profile.is_administrator():
        exams = ModelExam.objects.all()
    else:
        participant_exams = ModelExamParticipant.objects.filter(user=request.user).values_list("exam", flat=True)
        exams = ModelExam.objects.filter(id__in=participant_exams)

    if query:
        exams = exams.filter(Q(name__icontains=query) | Q(created_by__username__icontains=query))

    exams = order_queryset(exams, order_by)
    exams = paginate_queryset(exams, page, page_size)

    return [ExamSchema.from_orm(exam) for exam in exams]


@router.get("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_exam_details(request, exam_id: int):
    """
    Recupera detalhes de uma prova específico pelo ID.
    - Participantes só podem acessar provas em que estão inscritos.
    """
    is_authenticated(request)
    exam = get_object_or_404(ModelExam, id=exam_id)

    if not request.user.profile.is_administrator():
        if not ModelExamParticipant.objects.filter(exam=exam, user=request.user).exists():
            raise HttpError(403, ErrorSchema(detail="Permission denied"))

    return ExamSchema.from_orm(exam)


@router.patch("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def partial_update_exam(request, exam_id: int, data: ExamUpdateSchema):
    """
    Atualiza parcialmente uma prova (Apenas administradores).
    """
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    for attr, value in data.model_dump(exclude_unset=True).items():
        setattr(exam, attr, value)
    exam.save()
    return ExamSchema.from_orm(exam)


@router.put("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def full_update_exam(request, exam_id: int, payload: ExamUpdateSchema):
    """
    Atualiza completamente uma prova (Apenas administradores).
    """
    is_authenticated(request)
    is_admin(request)
    exam = get_object_or_404(ModelExam, id=exam_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(exam, attr, value)
    exam.save()
    return ExamSchema.from_orm(exam)


@router.delete("/{exam_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_exam(request, exam_id: int):
    """Apaga uma prova pelo seu ID (Apenas administradores)."""
    is_authenticated(request)
    is_admin(request)
    exam = get_object_or_404(ModelExam, id=exam_id)
    exam.delete()
    return 204, None



"""Gestão de Participantes"""

@router.get("/{exam_id}/participants/", response={200: list[ExamParticipantSchema], 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def list_participants(
    request,
    exam_id: int,
    query: str = None,
    order_by: str = "user__username",
    page: int = 1,
    page_size: int = 10,
):
    """
    Lista os participantes de uma prova com suporte a busca, ordenação e paginação.
    Apenas administradores podem acessar.
    """
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    participants = ModelExamParticipant.objects.filter(exam=exam)

    if query:
        participants = participants.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query)
        )

    participants = order_queryset(participants, order_by)

    participants = paginate_queryset(participants, page, page_size)

    return [ExamParticipantSchema.from_orm(participant) for participant in participants]


@router.post("/{exam_id}/participants/", response={200: ExamParticipantSchema, 400: ErrorSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def add_participant(request, exam_id: int, payload: ExamParticipantCreateSchema):
    """
    Adiciona um participante a uma prova (Apenas administradores).
    """
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    user = get_object_or_404(User, id=payload.user_id)

    participant, created = ModelExamParticipant.objects.get_or_create(exam=exam, user=user)
    if not created:
        raise HttpError(400, "User is already a participant in this exam")

    return ExamParticipantSchema.from_orm(participant)


@router.delete("/{exam_id}/participants/{user_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def remove_participant(request, exam_id: int, user_id: int):
    """
    Remove um participante de uma prova (Apenas administradores).
    """
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    participant = get_object_or_404(ModelExamParticipant, exam=exam, user_id=user_id)

    participant.delete()
    return 204, None


"""
Gestão de Questões
"""

@router.get("/{exam_id}/questions/", response={200: list[ExamQuestionSchema], 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def list_questions(
    request,
    exam_id: int,
    query: str = None,
    order_by: str = "question__text",
    page: int = 1,
    page_size: int = 10,
):
    """
    Lista as questões vinculadas a uma prova com suporte a busca, ordenação e paginação.
    """
    is_authenticated(request)

    exam = get_object_or_404(ModelExam, id=exam_id)

    if not request.user.profile.is_administrator():
        if not ModelExamParticipant.objects.filter(exam=exam, user=request.user).exists():
            raise HttpError(403, "Permission denied")

    questions = ModelExamQuestion.objects.filter(exam=exam)

    if query:
        questions = questions.filter(
            Q(question__text__icontains=query)
        )

    questions = order_queryset(questions, order_by)

    questions = paginate_queryset(questions, page, page_size)

    return [ExamQuestionSchema.from_orm(q) for q in questions]


@router.post("/{exam_id}/questions/", response={200: ExamQuestionSchema, 400: ErrorSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def add_question(request, exam_id: int, payload: ExamQuestionCreateSchema):
    """
    Adiciona uma questão a uma prova (Apenas administradores).
    """
    is_authenticated(request)
    is_admin(request)  # Verificação de permissão antes de processar o payload

    exam = get_object_or_404(ModelExam, id=exam_id)
    question = get_object_or_404(ModelQuestion, id=payload.question_id)

    exam_question, created = ModelExamQuestion.objects.get_or_create(exam=exam, question=question)
    if not created:
        raise HttpError(400, "Question is already linked to this exam")

    return ExamQuestionSchema.from_orm(exam_question)


@router.delete("/{exam_id}/questions/{question_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def remove_question(request, exam_id: int, question_id: int):
    """
    Remove uma questão de uma prova (Apenas administradores).
    """
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)
    exam_question = get_object_or_404(ModelExamQuestion, exam=exam, question_id=question_id)

    exam_question.delete()
    return 204, None