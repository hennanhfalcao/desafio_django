from celery import shared_task
from api.models import ModelParticipation, ModelAnswer, ModelChoice
from django.utils.timezone import now


@shared_task
def calculate_score(participation_id):
    """
    Calcula a pontuação para uma participação específica.
    """

    try:
        participation = ModelParticipation.objects.get(id=participation_id)

        if participation.finished_at:
            return f"Participação {participation_id} já foi finalizada."

        answers = participation.answer.all()
        total_questions = participation.exam.questions.count()
        correct_answers = 0

        for answer in answers:
            if answer.choice.is_correct:
                correct_answers += 1

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        participation.score = score
        participation.finished_at = now()
        participation.save()

        return f"Score calculado com sucesso para a participação {participation_id}: {score}%"
    except ModelParticipation.DoesNotExist:
        return f"Participação {participation_id} não encontrada."

    except Exception as e:
        return f"Erro ao calcular score para a participação {participation_id}: {str(e)}"