from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import (
    ModelExam,
    ModelParticipation,
    ModelQuestion,
    ModelChoice,
    ModelAnswer,
    ModelUserProfile,
)


class TestAnswerEndpoints(APITestCase):
    def setUp(self):
        # Criação de usuário participante
        self.participant_user = User.objects.create_user(
            username="participant",
            password="participant123",
            email="participant@example.com"
        )
        ModelUserProfile.objects.create(
            user=self.participant_user,
            is_admin=False,
            is_participant=True
        )

        # Criação de prova
        self.exam = ModelExam.objects.create(
            name="Prova 1",
            created_by=self.participant_user
        )

        # Criação de questão e associação à prova
        self.question = ModelQuestion.objects.create(text="Questão 1")
        self.exam.questions.add(self.question)  # Associa a questão ao exame

        # Criação de escolhas
        self.choice_correct = ModelChoice.objects.create(
            question=self.question,
            text="Opção Correta",
            is_correct=True
        )
        self.choice_incorrect = ModelChoice.objects.create(
            question=self.question,
            text="Opção Incorreta",
            is_correct=False
        )

        # Criação de participação
        self.participation = ModelParticipation.objects.create(
            user=self.participant_user,
            exam=self.exam
        )

        # Login do participante
        response = self.client.post(
            "/api/auth/login/",
            {"username": "participant", "password": "participant123"},
            format="json"
        )
        self.participant_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {response.json().get('access_token')}"
        }

    def test_list_answers(self):
        # Criação de resposta
        answer = ModelAnswer.objects.create(
            participation=self.participation,
            question=self.question,
            choice=self.choice_correct
        )

        response = self.client.get(
            f"/api/answers/?participation_id={self.participation.id}",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)
        self.assertEqual(response.json()["results"][0]["id"], answer.id)

    def test_create_answer(self):
        payload = {
            "participation_id": self.participation.id,
            "question_id": self.question.id,
            "choice_id": self.choice_correct.id
        }
        response = self.client.post(
            "/api/answers/",
            payload,
            **self.participant_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["choice"]["id"], self.choice_correct.id)

    def test_create_answer_invalid_choice(self):
        payload = {
            "participation_id": self.participation.id,
            "question_id": self.question.id,
            "choice_id": 9999  # Escolha inválida
        }
        response = self.client.post(
            "/api/answers/",
            payload,
            **self.participant_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_answer(self):
        answer = ModelAnswer.objects.create(
            participation=self.participation,
            question=self.question,
            choice=self.choice_incorrect
        )
        payload = {"choice_id": self.choice_correct.id}
        response = self.client.patch(
            f"/api/answers/patch/{answer.id}/",
            payload,
            **self.participant_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["choice"]["id"], self.choice_correct.id)

    def test_update_answer_invalid_choice(self):
        answer = ModelAnswer.objects.create(
            participation=self.participation,
            question=self.question,
            choice=self.choice_correct
        )
        payload = {"choice_id": 9999}  # Escolha inválida
        response = self.client.patch(
            f"/api/answers/patch/{answer.id}/",
            payload,
            **self.participant_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_answer(self):
        answer = ModelAnswer.objects.create(
            participation=self.participation,
            question=self.question,
            choice=self.choice_correct
        )
        response = self.client.delete(
            f"/api/answers/{answer.id}/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ModelAnswer.objects.filter(id=answer.id).exists())
