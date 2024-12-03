from rest_framework.test import APITestCase
from rest_framework import status
from api.models import ModelQuestion, ModelChoice, ModelExam
from django.contrib.auth import get_user_model

User = get_user_model()


class TestQuestionEndpoints(APITestCase):
    def setUp(self):
        # Criação de usuários
        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin123",
            email="admin@example.com",
            is_admin=True,
            is_participant=False
        )

        self.participant_user = User.objects.create_user(
            username="participant",
            password="participant123",
            email="participant@example.com",
            is_admin=False,
            is_participant=True
        )


        self.exam1 = ModelExam.objects.create(name="Prova 1", created_by=self.admin_user)
        self.exam2 = ModelExam.objects.create(name="Prova 2", created_by=self.admin_user)

        self.question1 = ModelQuestion.objects.create(text="Questão 1")
        self.question2 = ModelQuestion.objects.create(text="Questão 2")
        self.question1.exams.add(self.exam1)


        admin_login_response = self.client.post(
            "/api/token/",
            {"username": "admin", "password": "admin123"},
            format="json"
        )

        self.admin_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {admin_login_response.json().get('access')}"
        }

    def test_create_question(self):
        payload = {
            "text": "Nova Questão",
            "choices": [
                {"text": "Opção 1", "is_correct": False},
                {"text": "Opção 2", "is_correct": True},
            ]
        }
        response = self.client.post("/api/questions/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["text"], "Nova Questão")
        self.assertEqual(len(response.json()["choices"]), 2)

    def test_list_questions(self):
        response = self.client.get("/api/questions/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_list_questions_with_query(self):
        response = self.client.get("/api/questions/?query=Questão 1", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = response.json()
        self.assertTrue(any("Questão 1" in question["text"] for question in questions))

    def test_list_questions_with_ordering(self):
        response = self.client.get("/api/questions/?order_by=-created_at", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_question_details(self):
        response = self.client.get(f"/api/questions/{self.question1.id}", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], self.question1.text)
        self.assertIn(self.exam1.id, response.json()["exam_ids"])

    def test_partial_update_question(self):
        payload = {"text": "Questão Atualizada"}
        response = self.client.patch(f"/api/questions/{self.question1.id}/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "Questão Atualizada")

    def test_update_question(self):
        payload = {
            "text": "Questão Atualizada",
            "exam_ids": [self.exam2.id],
            "choices": [
                {"text": "Nova Opção 1", "is_correct": False},
                {"text": "Nova Opção 2", "is_correct": True},
            ]
        }
        response = self.client.put(f"/api/questions/{self.question1.id}/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "Questão Atualizada")
        self.assertEqual(len(response.json()["choices"]), 2)
        self.assertIn(self.exam2.id, response.json()["exam_ids"])

    def test_delete_question(self):
        response = self.client.delete(f"/api/questions/{self.question1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_link_question_to_exam(self):
        response = self.client.post(f"/api/questions/{self.question2.id}/{self.exam2.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.exam2.id, response.json()["exam_ids"])

    def test_unlink_question_from_exam(self):
        response = self.client.delete(f"/api/questions/{self.question1.id}/{self.exam1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.exam1.id, response.json()["exam_ids"])

    def test_list_questions_with_pagination(self):
        response = self.client.get("/api/questions/?page=1&page_size=1", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_questions_ordering_and_search(self):
        response = self.client.get("/api/questions/?order_by=text&query=Questão", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)