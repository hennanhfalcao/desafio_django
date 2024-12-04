from celery import shared_task
from api.models import ModelParticipation, ModelExam, ModelRanking
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
        
        answers = participation.answers.all()
        total_questions = participation.exam.questions.count()
        correct_answers = sum(1 for answer in answers if answer.choice.is_correct)

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        participation.score = score
        participation.finished_at = now()
        participation.save()

        generate_ranking.delay(participation.exam.id)

        return f"Score calculado com sucesso para a participação {participation_id}: {score}%"
    
    except ModelParticipation.DoesNotExist:
        return f"Participação {participation_id} não encontrada."
    
    except Exception as e:
        return f"Erro ao calcular score para a participação {participation_id}: {str(e)}"
    
@shared_task
def generate_ranking(exam_id):
    """
    Gera um ranking para uma prova específica.
    """

    try:
        exam = ModelExam.objects.get(id=exam_id)
        participations = (
            ModelParticipation.objects.filter(exam=exam, finished_at__isnull=False)
            .order_by("-score", "finished_at")
        )

        print(f"Participações encontradas para o ranking: {participations.count()}")

        ModelRanking.objects.filter(exam=exam).delete()

        rankings = [
            ModelRanking(
                exam=exam,
                participant=participation.user,
                score=participation.score,
                position=position,
            )
            for position, participation in enumerate(participations, start=1)
        ]

        ModelRanking.objects.bulk_create(rankings)
        print(f"Ranking criado com sucesso para o exame {exam_id}: {len(rankings)} entradas.")

        return f"Ranking gerado com sucesso para a prova {exam_id}."

    except ModelExam.DoesNotExist:
        return f"Prova {exam_id} não encontrada."

    except Exception as e:
        return f"Erro ao gerar ranking para a prova {exam_id}: {str(e)}"