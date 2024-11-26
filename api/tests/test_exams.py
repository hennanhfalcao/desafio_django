from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelUserProfile, ModelExam


class TestExamEndpoints(APITestCase):
    def setUp(self):
        # Criação de usuários
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

        # Obtenção de tokens
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

    def test_create_exam_as_admin(self):
        payload = {"name": "New Exam"}
        response = self.client.post("/api/exams/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("name"), "New Exam")
        self.assertEqual(response.json().get("created_by_id"), self.admin_user.id)

    def test_create_exam_as_participant(self):
        payload = {"name": "New Exam"}
        response = self.client.post("/api/exams/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get("detail"), "Permission denied")  # Compatível com utils.py

    def test_create_exam_unauthenticated(self):
        payload = {"name": "New Exam"}
        response = self.client.post("/api/exams/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get("detail"), "Authentication required")  # Compatível com utils.py

    def test_create_exam_missing_data(self):
        payload = {}  # Nome ausente
        response = self.client.post("/api/exams/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("name", [error["loc"][-1] for error in response.json().get("detail", [])])