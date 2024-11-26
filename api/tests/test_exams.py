from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelUserProfile, ModelExam


class TestExamEndpoints(APITestCase):
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

        self.exam = ModelExam.objects.create(name="Test Exam", created_by=self.admin_user)

        for i in range(15):
            ModelExam.objects.create(
                name=f"Exam {i+1}",
                created_by=self.admin_user
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
        self.assertEqual(response.json()["name"], "New Exam")

    def test_create_exam_as_participant(self):
        payload = {"name": "New Exam"}
        response = self.client.post("/api/exams/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_partial_update_exam_as_admin(self):
        payload = {"name": "Updated Exam Name"}
        response = self.client.patch(
            f"/api/exams/{self.exam.id}/",
            payload,
            **self.admin_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Updated Exam Name")

    def test_partial_update_exam_as_participant(self):
        payload = {"name": "Updated Exam Name"}
        response = self.client.patch(
            f"/api/exams/{self.exam.id}/",
            payload,
            **self.participant_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_delete_exam_as_admin(self):
        response = self.client.delete(f"/api/exams/{self.exam.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_exam_as_participant(self):
        response = self.client.delete(f"/api/exams/{self.exam.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_list_exams_pagination(self):
        """
        Testa a paginação de exames, verificando se o número correto de exames é retornado por página.
        """
        response = self.client.get('/api/exams/?page=1&page_size=5', **self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)

        response = self.client.get('/api/exams/?page=2&page_size=5', **self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)

        response = self.client.get('/api/exams/?page=3&page_size=5', **self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)

    def test_list_exams_ordering(self):
        """
        Testa a ordenação dos exames com base no campo `name` em ordem decrescente.
        """
        response = self.client.get('/api/exams/?ordering=-name', **self.admin_headers)
        self.assertEqual(response.status_code, 200)

        exams = response.json()
        self.assertTrue(exams[0]['name'] > exams[-1]['name'])

    def test_list_exams_search(self):
        """
        Testa a busca de exames com base no campo `name`.
        """
        response = self.client.get('/api/exams/?search=Exam 1', **self.admin_headers)
        self.assertEqual(response.status_code, 200)

        exams = response.json()
        self.assertTrue(any("Exam 1" in exam['name'] for exam in exams)) 