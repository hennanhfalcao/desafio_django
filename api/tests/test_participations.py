from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelParticipation, ModelExam, ModelUserProfile


class TestParticipationEndpoints(APITestCase):
    def setUp(self):
        # Configuração inicial de usuários e dados
        self.admin_user = User.objects.create_user(
            username="admin", password="admin123", email="admin@example.com"
        )
        ModelUserProfile.objects.create(
            user=self.admin_user, is_admin=True, is_participant=False
        )

        self.participant_user = User.objects.create_user(
            username="participant", password="participant123", email="participant@example.com"
        )
        ModelUserProfile.objects.create(
            user=self.participant_user, is_admin=False, is_participant=True
        )

        self.exam1 = ModelExam.objects.create(name="Exam 1", created_by=self.admin_user)
        self.exam2 = ModelExam.objects.create(name="Exam 2", created_by=self.admin_user)

        # Fazer login como admin e participante
        admin_login_response = self.client.post(
            "/api/auth/login/",
            {"username": "admin", "password": "admin123"},
            format="json",
        )
        self.admin_token = admin_login_response.json().get("access_token")

        participant_login_response = self.client.post(
            "/api/auth/login/",
            {"username": "participant", "password": "participant123"},
            format="json",
        )
        self.participant_token = participant_login_response.json().get("access_token")

        self.participation1 = ModelParticipation.objects.create(
            user=self.participant_user, exam=self.exam1, score=85.5
        )
        self.participation2 = ModelParticipation.objects.create(
            user=self.participant_user, exam=self.exam2, score=90.0
        )

        self.admin_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"
        }
        self.participant_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.participant_token}"
        }

    # ===========================
    # Testes de criação
    # ===========================
    def test_create_participation_as_admin(self):
        payload = {"exam_id": self.exam2.id, "user_id": self.participant_user.id}
        response = self.client.post(
            "/api/participations/", payload, **self.admin_headers, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["exam"]["id"], self.exam2.id)
        self.assertEqual(response.json()["user"]["id"], self.participant_user.id)

    def test_create_participation_as_participant(self):
        payload = {"exam_id": self.exam2.id, "user_id": self.participant_user.id}
        response = self.client.post(
            "/api/participations/", payload, **self.participant_headers, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_participation_invalid_exam(self):
        payload = {"exam_id": 9999, "user_id": self.participant_user.id}
        response = self.client.post(
            "/api/participations/", payload, **self.admin_headers, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_participation_invalid_user(self):
        payload = {"exam_id": self.exam2.id, "user_id": 9999}
        response = self.client.post(
            "/api/participations/", payload, **self.admin_headers, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ===========================
    # Testes de listagem
    # ===========================
    def test_list_participations_as_admin(self):
        response = self.client.get("/api/participations/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_list_participations_as_participant(self):
        response = self.client.get("/api/participations/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_list_participations_with_search(self):
        response = self.client.get(
            "/api/participations/?query=Exam 1", **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["exam"]["name"], "Exam 1")

    def test_list_participations_with_ordering(self):
        response = self.client.get(
            "/api/participations/?order_by=score", **self.admin_headers
        )
        participations = response.json()
        scores = [p["score"] for p in participations]
        self.assertTrue(all(scores[i] <= scores[i + 1] for i in range(len(scores) - 1)))

    def test_list_participations_with_pagination(self):
        response = self.client.get(
            "/api/participations/?page=1&page_size=1", **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    # ===========================
    # Testes de obtenção individual
    # ===========================
    def test_get_participation_as_admin(self):
        response = self.client.get(
            f"/api/participations/{self.participation1.id}/", **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.participation1.id)

    def test_get_participation_as_participant(self):
        response = self.client.get(
            f"/api/participations/{self.participation1.id}/",
            **self.participant_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_nonexistent_participation(self):
        response = self.client.get("/api/participations/9999/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ===========================
    # Testes de atualização
    # ===========================
    def test_update_participation_as_admin(self):
        payload = {"score": 95.0, "finished_at": "2024-12-31T23:59:59Z"}
        response = self.client.put(
            f"/api/participations/{self.participation1.id}/",
            payload,
            **self.admin_headers,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["score"], 95.0)

    def test_partial_update_participation_as_admin(self):
        payload = {"score": 90.0}
        response = self.client.patch(
            f"/api/participations/{self.participation1.id}/",
            payload,
            **self.admin_headers,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["score"], 90.0)

    def test_update_participation_as_participant(self):
        payload = {"score": 95.0}
        response = self.client.put(
            f"/api/participations/{self.participation1.id}/",
            payload,
            **self.participant_headers,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ===========================
    # Testes de exclusão
    # ===========================
    def test_delete_participation_as_admin(self):
        response = self.client.delete(
            f"/api/participations/{self.participation1.id}/", **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ModelParticipation.objects.filter(id=self.participation1.id).exists()
        )

    def test_delete_participation_as_participant(self):
        response = self.client.delete(
            f"/api/participations/{self.participation1.id}/",
            **self.participant_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_participation(self):
        response = self.client.delete("/api/participations/9999/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)