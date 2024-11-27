from ninja import Router
from django.db.models import Q
from api.models import ModelExam
from api.schemas import ExamSchema, ExamCreateSchema, ExamUpdateSchema, ErrorSchema
from api.utils import is_authenticated, is_admin, paginate_queryset, order_queryset
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

router = Router(tags=["Exams"])

@router.post("/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_exam(request, payload: ExamCreateSchema):
    """Cria uma nova prova"""
    is_authenticated(request)
    is_admin(request)
    exam = ModelExam.objects.create(name=payload.name, created_by=request.user)
    return ExamSchema.from_orm(exam)

@router.get("/", response={200: list[ExamSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_exams(
    request, 
    query: str = None, 
    order_by: str = "id", 
    page: int = 1, 
    page_size: int = 10
):
    """
    Lista todos os exames com busca, ordenação e paginação opcionais.
    """
    is_authenticated(request)

    exams = ModelExam.objects.all()
    if query:
        exams = exams.filter(Q(name__icontains=query) | Q(created_by__username__icontains=query))

    exams = order_queryset(exams, order_by)

    exams = paginate_queryset(exams, page, page_size)

    return [ExamSchema.from_orm(exam) for exam in exams]

@router.get("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_exam_details(request, exam_id: int):
    """Recupera detalhes de uma prova específico pelo ID."""
    is_authenticated(request)
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="Exam not found"))
    return ExamSchema.from_orm(exam)

@router.patch(
    "/{exam_id}/",
    response={200: ExamSchema, 403: ErrorSchema, 422: ErrorSchema},
    auth=None
)
def partial_update_exam(request, exam_id: int, data: ExamUpdateSchema):
    """
    Atualiza parcialmente um exame.
    """
    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id)

    for attr, value in data.model_dump(exclude_unset=True).items():
        setattr(exam, attr, value)

    exam.save()
    return 200, ExamSchema.from_orm(exam)

@router.put("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def full_update_exam(request, exam_id: int, payload: ExamUpdateSchema):
    """Atualiza completamente uma prova."""
    is_authenticated(request)
    is_admin(request)
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="Exam not found"))
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(exam, attr, value)
    exam.save()
    return ExamSchema.from_orm(exam)

@router.delete("/{exam_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_exam(request, exam_id: int):
    """Apaga uma prova pelo seu ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="Exam not found"))
    exam.delete()
    return 204, None