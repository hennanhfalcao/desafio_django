from rest_framework.test import APITestCase
from rest_framework import status
from api.models import (
    ModelExam,
    ModelParticipation,
    ModelQuestion,
    ModelChoice,
    ModelAnswer,
)
from django.contrib.auth import get_user_model
User = get_user_model()

class TestAnswerEndpoints(APITestCase):
    def setUp(self):
        self.participant_user = User.objects.create_user(
            username="participant",
            password="participant123",
            email="participant@example.com",
            is_admin=False,
            is_participant=True
        )

        self.exam = ModelExam.objects.create(
            name="Prova 1",
            created_by=self.participant_user
        )

        self.question = ModelQuestion.objects.create(text="Questão 1")
        self.exam.questions.add(self.question)  # Associa a questão ao exame

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

        self.participation = ModelParticipation.objects.create(
            user=self.participant_user,
            exam=self.exam
        )


        response = self.client.post(
            "/api/token/",
            {"username": "participant", "password": "participant123"},
            format="json"
        )
        self.participant_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {response.json().get('access')}"
        }

    def test_list_answers(self):
        answer = ModelAnswer.objects.create(
            participation=self.participation,
            question=self.question,
            choice=self.choice_correct
        )

        response = self.client.get(
            f"/api/answers/participants/{self.participation.id}/",
            **self.participant_headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data), 1)  # 

        response_answer = response_data[0]
        self.assertEqual(response_answer["id"], answer.id)
        self.assertEqual(response_answer["participation"]["id"], self.participation.id)
        self.assertEqual(response_answer["question"]["id"], self.question.id)
        self.assertEqual(response_answer["choice"]["id"], self.choice_correct.id)

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
            "choice_id": 9999
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
            f"/api/answers/{answer.id}/",
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
        payload = {"choice_id": 9999} 
        response = self.client.patch(
            f"/api/answers/{answer.id}/",
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
