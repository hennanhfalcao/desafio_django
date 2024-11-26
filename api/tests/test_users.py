from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelUserProfile


class TestUserEndpoints(APITestCase):
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

    def test_create_user_as_admin(self):
        payload = {
            "username": "new_user",
            "password": "newpassword123",
            "email": "new_user@example.com",
            "is_admin": False,
            "is_participant": True
        }
        response = self.client.post("/api/users/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "new_user")

    def test_create_user_as_participant(self):
        payload = {
            "username": "new_user",
            "password": "newpassword123",
            "email": "new_user@example.com",
            "is_admin": False,
            "is_participant": True
        }
        response = self.client.post("/api/users/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_list_users_as_admin(self):
        response = self.client.get("/api/users/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_as_participant(self):
        response = self.client.get("/api/users/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_partial_update_user_as_admin(self):
        payload = {
            "username": "updated_username",
            "email": "updated_email@example.com",
            "password": "newpassword123",
            "is_admin": False,
            "is_participant": True
        }
        response = self.client.patch(
            f"/api/users/{self.participant_user.id}/",
            payload,
            **self.admin_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "updated_email@example.com")

    def test_partial_update_user_with_invalid_data(self):
        payload = {"email": "invalid-email"}  # Email inválido
        response = self.client.patch(
            f"/api/users/{self.participant_user.id}/",
            payload,
            **self.admin_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn(
            "value is not a valid email address: An email address must have an @-sign.",
            str(response.json())
        )

    def test_partial_update_user_as_participant(self):
    # Payload contendo dados mínimos válidos e consistentes
        payload = {
            "username": "updated_participant_username",
            "password": "newpassword123",
            "email": "updated_participant@example.com",
            "is_admin": False,  # O participante não deve ter privilégios de admin
            "is_participant": True,  # O participante continua como participante
        }
        response = self.client.patch(
            f"/api/users/{self.admin_user.id}/",  # Tentativa de alterar outro usuário (admin)
            payload,
            **self.participant_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_delete_user_as_admin(self):
        response = self.client.delete(f"/api/users/{self.participant_user.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_as_participant(self):
        response = self.client.delete(f"/api/users/{self.admin_user.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")