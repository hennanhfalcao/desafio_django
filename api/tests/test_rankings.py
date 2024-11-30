from django.test import TestCase
from api.models import ModelExam, ModelParticipation, ModelRanking
from django.contrib.auth.models import User
from api.tasks import generate_ranking


class TestRankings(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username="admin", password="admin123")
        self.exam = ModelExam.objects.create(name="Prova 1", created_by=self.admin_user)

    def test_generate_ranking(self):
        participants = [
            User.objects.create_user(username=f"user{i}", password="user123")
            for i in range(3)
        ]

        participations = [
            ModelParticipation(
                user=participant,
                exam=self.exam,
                score=100 - (idx * 10),  # Pontuações decrescentes
                finished_at="2024-11-30T00:00:00Z",
            )
            for idx, participant in enumerate(participants)
        ]

        ModelParticipation.objects.bulk_create(participations)

        # Executa a task de geração de ranking
        generate_ranking(self.exam.id)

        rankings = ModelRanking.objects.filter(exam=self.exam).order_by("position")
        self.assertEqual(rankings.count(), 3)
        self.assertEqual(rankings[0].position, 1)