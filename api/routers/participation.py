from typing import List
from ninja import Router
from api.models import ModelParticipation, ModelExam
from api.schemas import ParticipationSchema, ParticipationCreateSchema
from django.db.models import Q


router = Router()

@router.post("/", response=ParticipationSchema)
def create_participation(request, data: ParticipationCreateSchema):
    if not ModelExam.objects.filter(id=data.exam_id).exists():
        return {"detail":"Invalid exam ID"}, 400
    
    participation = ModelParticipation.objects.create(
        user = request.user,
        exam_id=data.exam_id
    )
    return ParticipationSchema.from_orm(participation)

@router.get("/", response=List[ParticipationSchema])
def list_participations(request, query: str = None, exam_id: int = None, order_by: str = "-started_at", page: int = 1, page_size: int = 10):
    participations = ModelParticipation.objects.all()

    if exam_id is not None:
        if not ModelExam.objects.filter(id=exam_id).exists():
            return {"detail":"Invalid exam ID"}, 400
        participations = participations.filter(exam_id=exam_id)

    if query:
        participations = participations.filter(
            Q(user__username_icontains=query) |
            Q(exam__name__icontains=query)
        )

    participations = participations.order_by(order_by)
    start = (page-1)*page_size
    end = start + page_size

    return participations[start:end]