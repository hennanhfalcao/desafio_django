from django.test import TestCase
from api.models import ModelExam, ModelParticipation, ModelRanking
from api.tasks import generate_ranking
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRankings(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin123",
            email="admin@example.com"
        )
        # Cria o exame associado ao administrador
        self.exam = ModelExam.objects.create(name="Prova 1", created_by=self.admin_user)

    def test_generate_ranking(self):
 
        participants = [
            User.objects.create_user(
                username=f"user{i}",
                password="user123",
                email=f"user{i}@example.com"
            )
            for i in range(3)
        ]

        participations = [
            ModelParticipation(
                user=participant,
                exam=self.exam,
                score=100 - (idx * 10),
                finished_at="2024-11-30T00:00:00Z",
            )
            for idx, participant in enumerate(participants)
        ]

        ModelParticipation.objects.bulk_create(participations)


        generate_ranking(self.exam.id)

        rankings = ModelRanking.objects.filter(exam=self.exam).order_by("position")
        self.assertEqual(rankings.count(), 3)

        self.assertEqual(rankings[0].position, 1)
        self.assertEqual(rankings[0].participant.username, "user0")
        self.assertEqual(rankings[1].position, 2)
        self.assertEqual(rankings[2].position, 3)