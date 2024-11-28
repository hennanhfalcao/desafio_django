from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelQuestion, ModelExam, ModelUserProfile, ModelExamQuestion


class TestQuestionEndpoints(APITestCase):
    def setUp(self):
        # Criar usuários
        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin123",
            email="admin@example.com"
        )
        ModelUserProfile.objects.create(
            user=self.admin_user,
            is_admin=True,
            is_participant=False
        )

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

        # Criar exames
        self.exam1 = ModelExam.objects.create(name="Exam 1", created_by=self.admin_user)
        self.exam2 = ModelExam.objects.create(name="Exam 2", created_by=self.admin_user)

        # Criar questões
        self.question1 = ModelQuestion.objects.create(text="Question 1")
        self.question2 = ModelQuestion.objects.create(text="Another Question")
        self.question3 = ModelQuestion.objects.create(text="Sample Question")
        ModelExamQuestion.objects.create(exam=self.exam1, question=self.question1)

        # Login e tokens
        admin_login_response = self.client.post(
            "/api/auth/login/",
            {"username": "admin", "password": "admin123"},
            format="json"
        )
        participant_login_response = self.client.post(
            "/api/auth/login/",
            {"username": "participant", "password": "participant123"},
            format="json"
        )

        self.admin_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {admin_login_response.json().get('access_token')}"
        }
        self.participant_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {participant_login_response.json().get('access_token')}"
        }

    # ============================
    # Testes de criação de questões
    # ============================
    def test_create_question_as_admin(self):
        payload = {"text": "New Question", "exams": [self.exam1.id, self.exam2.id]}
        response = self.client.post("/api/questions/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "New Question")
        self.assertEqual(response.json()["exams"], [self.exam1.id, self.exam2.id])

    def test_create_question_as_participant(self):
        payload = {"text": "New Question", "exams": [self.exam1.id]}
        response = self.client.post("/api/questions/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ============================
    # Testes de listagem de questões
    # ============================
    def test_list_all_questions_as_admin(self):
        response = self.client.get("/api/questions/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 3)

    def test_list_all_questions_as_participant(self):
        response = self.client.get("/api/questions/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_questions_with_search(self):
        response = self.client.get("/api/questions/?query=Sample", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["text"], "Sample Question")

    def test_list_questions_with_ordering(self):
        response = self.client.get("/api/questions/?order_by=text", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = response.json()
        texts = [q["text"] for q in questions]
        self.assertTrue(all(texts[i] <= texts[i + 1] for i in range(len(texts) - 1)))

    def test_list_questions_with_pagination(self):
        response = self.client.get("/api/questions/?page=1&page_size=2", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    # ============================
    # Testes de obtenção de questão
    # ============================
    def test_get_question_as_admin(self):
        response = self.client.get(f"/api/questions/{self.question1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], self.question1.text)
        self.assertEqual(response.json()["exams"], [self.exam1.id])

    def test_get_question_as_participant(self):
        response = self.client.get(f"/api/questions/{self.question1.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexistent_question(self):
        response = self.client.get("/api/questions/9999/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ============================
    # Testes de atualização de questão
    # ============================
    def test_update_question_as_admin(self):
        payload = {"text": "Updated Question", "exams": [self.exam2.id]}
        response = self.client.put(f"/api/questions/{self.question1.id}/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "Updated Question")
        self.assertEqual(response.json()["exams"], [self.exam2.id])

    def test_update_question_as_participant(self):
        payload = {"text": "Updated Question"}
        response = self.client.put(f"/api/questions/{self.question1.id}/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_question(self):
        payload = {"text": "Updated Question"}
        response = self.client.put("/api/questions/9999/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ============================
    # Testes de exclusão de questão
    # ============================
    def test_delete_question_as_admin(self):
        response = self.client.delete(f"/api/questions/{self.question1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ModelQuestion.objects.filter(id=self.question1.id).exists())

    def test_delete_question_as_participant(self):
        response = self.client.delete(f"/api/questions/{self.question1.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_question(self):
        response = self.client.delete("/api/questions/9999/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)