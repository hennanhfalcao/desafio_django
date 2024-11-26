from ninja import Router
from django.db.models import Q
from api.models import ModelExam
from api.schemas import ExamSchema, ExamCreateSchema, ExamUpdateSchema, ErrorSchema
from api.utils import is_authenticated, is_admin
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404

router = Router(tags=["Exams"])

@router.post("/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_exam(request, payload: ExamCreateSchema):
    """Create a new exam."""
    is_authenticated(request)
    is_admin(request)
    exam = ModelExam.objects.create(name=payload.name, created_by=request.user)
    return ExamSchema.from_orm(exam)

@router.get("/", response={200: list[ExamSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_exams(request, search: str = None, ordering: str = "id"):
    """List all exams with optional search and ordering."""
    is_authenticated(request)
    exams = ModelExam.objects.all()
    if search:
        exams = exams.filter(Q(name__icontains=search) | Q(created_by__username__icontains=search))
    exams = exams.order_by(ordering)
    return [ExamSchema.from_orm(exam) for exam in exams]

@router.get("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_exam_details(request, exam_id: int):
    """Retrieve details of a specific exam by ID."""
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

    # Atualiza apenas os campos definidos no payload
    for attr, value in data.model_dump(exclude_unset=True).items():  # Alterado para `model_dump`
        setattr(exam, attr, value)

    exam.save()
    return 200, ExamSchema.from_orm(exam)

@router.put("/{exam_id}/", response={200: ExamSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def full_update_exam(request, exam_id: int, payload: ExamUpdateSchema):
    """Fully update an exam."""
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
    """Delete an exam by ID."""
    is_authenticated(request)
    is_admin(request)
    try:
        exam = ModelExam.objects.get(id=exam_id)
    except ModelExam.DoesNotExist:
        raise HttpError(404, ErrorSchema(detail="Exam not found"))
    exam.delete()
    return 204, None