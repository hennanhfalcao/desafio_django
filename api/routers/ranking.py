from django.shortcuts import get_object_or_404
from ninja import Router
from api.models import ModelExam, ModelRanking
from api.schemas import RankingSchema, ErrorSchema
from api.utils import is_admin, is_authenticated
from ninja.errors import HttpError

router = Router(tags=["Ranking"])

@router.get("/exams/{exam_id}/", response={200: list[RankingSchema], 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_ranking(request, exam_id: int):
    """
    Obtem o ranking de uma prova.
    Apenas administradores tem permissão
    """

    is_authenticated(request)
    is_admin(request)

    exam = get_object_or_404(ModelExam, id=exam_id) 
    rankings = ModelRanking.objects.filter(exam=exam).order_by("position")
    if not rankings.exists():
        raise HttpError(404, "Ranking não encontrado")
    
    return [
    RankingSchema.model_validate({
        "id": ranking.id,
        "exam_id": ranking.exam_id,
        "participant_id": ranking.participant.id,
        "participant_username": ranking.participant.username,
        "score": ranking.score,
        "position": ranking.position,
    })
    for ranking in rankings
    ]   