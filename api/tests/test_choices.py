from rest_framework.test import APITestCase
from rest_framework import status
from api.models import ModelChoice, ModelQuestion
from django.contrib.auth.models import User
from api.models import ModelUserProfile


class TestChoiceEndpoints(APITestCase):
    def setUp(self):
        # Criando usuários de teste
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

        # Criando questões de teste
        self.question = ModelQuestion.objects.create(text="Sample Question")

        # Criando alternativas de teste
        self.choice = ModelChoice.objects.create(
            question=self.question,
            text="Sample Choice",
            is_correct=True
        )

        # Obtendo tokens de autenticação
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

    def test_create_choice_as_admin(self):
        payload = {
            "question_id": self.question.id,
            "text": "New Choice",
            "is_correct": False
        }
        response = self.client.post("/api/choices/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "New Choice")
        self.assertEqual(response.json()["is_correct"], False)

    def test_create_choice_as_participant(self):
        payload = {
            "question_id": self.question.id,
            "text": "New Choice",
            "is_correct": False
        }
        response = self.client.post("/api/choices/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_get_choice_as_admin(self):
        response = self.client.get(f"/api/choices/{self.choice.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], self.choice.text)

    def test_get_choice_as_participant(self):
        response = self.client.get(f"/api/choices/{self.choice.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_update_choice_as_admin(self):
        payload = {
            "text": "Updated Choice",
            "is_correct": False
        }
        response = self.client.put(f"/api/choices/{self.choice.id}/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "Updated Choice")
        self.assertEqual(response.json()["is_correct"], False)

    def test_partial_update_choice_as_admin(self):
        payload = {"text": "Partially Updated Choice"}
        response = self.client.patch(f"/api/choices/{self.choice.id}/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "Partially Updated Choice")

    def test_update_choice_as_participant(self):
        payload = {
            "text": "Updated Choice",
            "is_correct": False
        }
        response = self.client.put(f"/api/choices/{self.choice.id}/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_delete_choice_as_admin(self):
        response = self.client.delete(f"/api/choices/{self.choice.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ModelChoice.objects.filter(id=self.choice.id).exists())

    def test_delete_choice_as_participant(self):
        response = self.client.delete(f"/api/choices/{self.choice.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")