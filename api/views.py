from ninja import NinjaAPI
from api.models import ModelExam
from typing import List

api = NinjaAPI()

@api.get("/exams", response=List[str])
def list_exams(request):
    return list(ModelExam.objects.values_list('name', flat=True))