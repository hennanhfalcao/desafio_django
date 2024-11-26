from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelUserProfile


class TestUserEndpoints(APITestCase):
    def setUp(self):
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

        self.admin_token = admin_login_response.json().get("access_token")
        self.participant_token = participant_login_response.json().get("access_token")

        self.admin_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"}
        self.participant_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.participant_token}"}

    def test_create_user(self):
        payload = {
            "username": "new_user",
            "password": "newpassword123",
            "email": "new_user@example.com",
            "is_admin": False,
            "is_participant": True
        }
        response = self.client.post("/api/users/", payload, **self.admin_headers, format="json")
        print("Create User Response:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_as_admin(self):
        response = self.client.get("/api/users/", **self.admin_headers)
        print("List Users as Admin Response:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_as_participant(self):
        response = self.client.get("/api/users/", **self.participant_headers)
        print("List Users as Participant Response:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_details_as_admin(self):
        response = self.client.get(f"/api/users/{self.participant_user.id}/", **self.admin_headers)
        print("Get User Details as Admin Response:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_details_as_participant(self):
        response = self.client.get(f"/api/users/{self.admin_user.id}/", **self.participant_headers)
        print("Get User Details as Participant Response:", response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_as_admin(self):
        payload = {
            "username": "updated_admin",
            "password": "newpass123",
            "email": "updated_admin@example.com",
            "is_admin": True,
            "is_participant": False
        }
        response = self.client.put(f"/api/users/{self.participant_user.id}/", payload, **self.admin_headers, format="json")
        print("Update User as Admin Response:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_as_admin(self):
        response = self.client.delete(f"/api/users/{self.participant_user.id}/", **self.admin_headers)
        print("Delete User as Admin Response:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)