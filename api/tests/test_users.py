from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserEndpoints(APITestCase):
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

        for i in range(15):
            User.objects.create_user(
                username=f"user{i+1}",
                password="password123",
                email=f"user{i+1}@example.com"
            )
        
        for user in User.objects.all():
            User.objects.get_or_create(username=user.username, email=user.email)

        admin_login_response = self.client.post(
            "/api/token/",
            {"username": "admin", "password": "admin123"},
            format="json"
        )
        participant_login_response = self.client.post(
            "/api/token/",
            {"username": "participant", "password": "participant123"},
            format="json"
        )

        self.admin_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {admin_login_response.json().get('access')}"
        }
        self.participant_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {participant_login_response.json().get('access')}"
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
        self.assertEqual(response.json()["username"], "updated_username")

    def test_partial_update_user_with_invalid_data(self):
        payload = {"email": "invalid-email"}  
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
        payload = {
            "username": "updated_participant_username",
            "password": "newpassword123",
            "email": "updated_participant@example.com",
            "is_admin": False, 
            "is_participant": True,  
        }
        response = self.client.patch(
            f"/api/users/{self.admin_user.id}/",
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
    
    def test_list_users_pagination(self):
        """
        Testa a paginação de usuários, verificando se o número correto de usuários é retornado por página.
        """
        response = self.client.get('/api/users/?page=1&page_size=5', **self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)

        response = self.client.get('/api/users/?page=2&page_size=5', **self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5) 

        response = self.client.get('/api/users/?page=3&page_size=5', **self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)

    def test_list_users_ordering(self):
        """
        Testa a ordenação dos usuários com base no campo `username` em ordem decrescente.
        """
        response = self.client.get('/api/users/?order_by=-username', **self.admin_headers)
        self.assertEqual(response.status_code, 200)

        users = response.json()
        self.assertTrue(users[0]['username'] > users[-1]['username'])

    def test_list_users_search(self):
        """
        Testa a busca de usuários com base no campo `username`.
        """
        response = self.client.get('/api/users/?search=user1', **self.admin_headers)
        self.assertEqual(response.status_code, 200)

        users = response.json()
        self.assertTrue(any("user1" in user['username'] for user in users))