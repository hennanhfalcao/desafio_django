from typing import List
from ninja import Router
from api.models import ModelAnswer, ModelParticipation, ModelQuestion, ModelChoice
from api.schemas import AnswerSchema, AnswerCreateSchema
from django.db.models import Q


router = Router()

@router.post("/", response=AnswerSchema)
def create_answer(request, data: AnswerCreateSchema):
    if not ModelParticipation.objects.filter(id=data.participation_id).exists():
        return {"detail":"Invalid participation ID"}, 400
    
    if not ModelQuestion.objects.filter(id=data.question_id).exists():
        return {"detail":"Invalid question ID"}, 400
    
    if not ModelChoice.objects.filter(id=data.choice_id).exists():
        return {"detail":"Invalid choice ID"}, 400
    
    answer = ModelAnswer.objects.create(
        participation_id=data.participation_id,
        question_id=data.question_id,
        choice_id=data.choice_id
    )
    return AnswerSchema.from_orm(answer)

@router.get("/",response=List[AnswerSchema])
def list_answers(request, query: str = None, participation_id:int=None, order_by:str="answered_at", page:int=1, page_size:int=10):
    answers = ModelAnswer.objects.all()

    if participation_id is not None:
        if not ModelParticipation.objects.filter(id=participation_id).exists():
            return {"detail":"Invalid participation ID"}, 400
        answers = answers.filter(participation_id=participation_id)

    if query:
        answers = answers.filter(
            Q(question__text__icontains=query) |
            Q(choice__text__icontains=query)
        )

    answers = answers.order_by(order_by)
    start = (page - 1) * page_size
    end = start + page_size

    return answers[start:end]    