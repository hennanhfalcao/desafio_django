from celery import shared_task
from api.models import ModelParticipation

@shared_task
def calculate_score(participation_id):
    participation = ModelParticipation.objects.get(id=participation_id)
    # Lógica de cálculo da pontuação
    score = 100  # Exemplo
    participation.score = score
    participation.save()
    return f'Score for participation {participation_id} calculated successfully!'