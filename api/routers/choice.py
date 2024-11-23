from typing import List
from ninja import Router
from api.models import ModelChoice, ModelQuestion
from api.schemas import ChoicesSchema, ChoicesCreateSchema
from django.db.models import Q


router = Router()

@router.post("/", response=ChoicesSchema)
def create_choice(request, data: ChoicesCreateSchema):
    choice = ModelChoice.objects.create(
        question_id=data.question_id,
        text=data.text,
        is_correct=data.is_correct
    )
    return ChoicesSchema.from_orm(choice)


@router.get("/", response=List[ChoicesSchema])
def list_choices(request, query: str = None, question_id: int = None, order_by: str = "text", page: int = 1, page_size: int = 10):
    choices = ModelChoice.objects.all()

    if question_id is not None:
        if not ModelQuestion.objects.filter(id=question_id).exists():
            return {"detail": "Invalid question ID"}, 400
        choices = choices.filter(question_id=question_id)

    if query:
        choices = choices.filter(Q(text_icontains=query)) 
    
    choices = choices.order_by(order_by)
    start = (page-1)*page_size
    end = start + page_size


    return choices[start:end]