from datetime import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelExam, ModelParticipation, ModelUserProfile
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from unittest.mock import patch
from api.tasks import calculate_score

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

        # Criação de provas
        self.exam1 = ModelExam.objects.create(name="Prova 1", created_by=self.admin_user)
        self.exam2 = ModelExam.objects.create(name="Prova 2", created_by=self.admin_user)


        # Registro do admin e participante
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
        payload = {"name": "Nova Prova"}
        response = self.client.post("/api/exams/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], "Nova Prova")

    def test_create_exam_as_participant(self):
        payload = {"name": "Nova Prova"}
        response = self.client.post("/api/exams/", payload, **self.participant_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_list_exams_as_admin(self):
        response = self.client.get("/api/exams/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_list_exams_with_query(self):
        response = self.client.get("/api/exams/?query=Prova 1", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exams = response.json()
        self.assertTrue(any("Prova 1" in exam["name"] for exam in exams))

    def test_list_exams_with_ordering(self):
        response = self.client.get("/api/exams/?order_by=-name", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exams = response.json()
        self.assertTrue(exams[0]["name"] > exams[-1]["name"])

    def test_get_exam_details_as_admin(self):
        response = self.client.get(f"/api/exams/{self.exam1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], self.exam1.name)

    def test_get_exam_details_as_participant(self):
        ModelParticipation.objects.create(user=self.participant_user, exam=self.exam1)
        response = self.client.get(f"/api/exams/{self.exam1.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_exam_details_as_unauthorized_user(self):
        response = self.client.get(f"/api/exams/{self.exam1.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_exam_as_admin(self):
        payload = {"name": "Prova Atualizada"}
        response = self.client.put(f"/api/exams/put/{self.exam1.id}/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Prova Atualizada")

    def test_partial_update_exam_as_admin(self):
        payload = {"name": "Prova Parcialmente Atualizada"}
        response = self.client.patch(f"/api/exams/patch/{self.exam1.id}/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Prova Parcialmente Atualizada")

    def test_delete_exam_as_admin(self):
        response = self.client.delete(f"/api/exams/{self.exam1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_exam_as_participant(self):
        response = self.client.delete(f"/api/exams/{self.exam1.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_list_participants_as_admin(self):
        ModelParticipation.objects.create(user=self.participant_user, exam=self.exam1)
        response = self.client.get(f"/api/exams/{self.exam1.id}/participants/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        participants = response.json()
        self.assertTrue(any(self.participant_user.username == p["user"]["username"] for p in participants))

    def test_create_participation_as_admin(self):
        payload = {"user_id": self.participant_user.id, "exam_id": self.exam1.id}
        response = self.client.post(f"/api/exams/{self.exam1.id}/participants/", payload, **self.admin_headers, format="json")
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["user"]["id"], self.participant_user.id)

    def test_create_participation_for_existing_user(self):
        ModelParticipation.objects.create(user=self.participant_user, exam=self.exam1)
        payload = {"user_id": self.participant_user.id, "exam_id": self.exam1.id}
        response = self.client.post(f"/api/exams/{self.exam1.id}/participants/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json()["detail"], "Usuário ja inscrito na prova")

    def test_delete_participation_as_admin(self):
        participation = ModelParticipation.objects.create(user=self.participant_user, exam=self.exam1)
        response = self.client.delete(
            f"/api/exams/{self.exam1.id}/participants/{self.participant_user.id}/",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ModelParticipation.objects.filter(id=participation.id).exists())

    def test_delete_participation_as_participant(self):
        ModelParticipation.objects.create(user=self.participant_user, exam=self.exam1)
        response = self.client.delete(
            f"/api/exams/{self.exam1.id}/participants/{self.participant_user.id}/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    def test_delete_nonexistent_participation(self):
        response = self.client.delete(
            f"/api/exams/{self.exam1.id}/participants/{self.participant_user.id}/",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Participação nao encontrada")

    def test_delete_participation_with_invalid_user(self):
        response = self.client.delete(
            f"/api/exams/{self.exam1.id}/participants/9999/", 
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Usuário nao encontrado")

    def test_delete_participation_with_invalid_exam(self):
        response = self.client.delete(
            f"/api/exams/9999/participants/{self.participant_user.id}/",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Prova nao encontrada")

    def test_get_participation_details_as_admin(self):
        participation = ModelParticipation.objects.create(
            user=self.participant_user,
            exam=self.exam1,
            started_at=make_aware(datetime(2024, 11, 29, 12, 0, 0)),
            finished_at=None,
            score=0.0
        )
        
        response = self.client.get(
            f"/api/exams/{self.exam1.id}/participants/{self.participant_user.id}/",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["user"]["id"], self.participant_user.id)
        self.assertEqual(response.json()["exam"]["id"], self.exam1.id)


    def test_get_participation_details_as_participant(self):
        participation = ModelParticipation.objects.create(
            user=self.participant_user,
            exam=self.exam1,
            started_at=make_aware(datetime(2024, 11, 29, 12, 0, 0)),
            finished_at=None,
            score=0.0
        )

        response = self.client.get(
            f"/api/exams/{self.exam1.id}/participants/{self.participant_user.id}/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")


    def test_update_participation_as_admin(self):
        participation = ModelParticipation.objects.create(
            user=self.participant_user,
            exam=self.exam1,
            started_at=make_aware(datetime(2024, 11, 29, 12, 0, 0)),  # Criação inicial
            finished_at=None,
            score=0.0
        )
        payload = {
            "started_at": "2024-11-29T14:00:00Z",  # UTC
            "finished_at": "2024-11-29T16:00:00Z",  # UTC
            "score": 95.5
        }
        response = self.client.patch(
            f"/api/exams/{self.exam1.id}/participants/{self.participant_user.id}/",
            payload,
            **self.admin_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Normalizar as datas recebidas no formato UTC para comparação
        started_at_response = parse_datetime(response.json()["started_at"])
        finished_at_response = parse_datetime(response.json()["finished_at"])

        self.assertEqual(started_at_response, parse_datetime(payload["started_at"]))
        self.assertEqual(finished_at_response, parse_datetime(payload["finished_at"]))
        self.assertEqual(response.json()["score"], payload["score"])


    def test_update_participation_as_participant(self):
        participation = ModelParticipation.objects.create(
            user=self.participant_user,
            exam=self.exam1,
            started_at=make_aware(datetime(2024, 11, 29, 12, 0, 0)),
            finished_at=None,
            score=0.0
        )
        payload = {"score": 50.0}
        response = self.client.patch(
            f"/api/exams/{self.exam1.id}/participants/{self.participant_user.id}/",
            payload,
            **self.participant_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")


    def test_update_participation_with_invalid_user(self):
        payload = {"score": 80.0}
        response = self.client.patch(
            f"/api/exams/{self.exam1.id}/participants/9999/",
            payload,
            **self.admin_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Usuário nao encontrado")


    def test_update_participation_with_invalid_exam(self):
        payload = {"score": 80.0}
        response = self.client.patch(
            f"/api/exams/9999/participants/{self.participant_user.id}/",
            payload,
            **self.admin_headers,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Prova nao encontrada")


    @patch("api.tasks.calculate_score.delay")  # Mocka a tarefa Celery
    def test_finish_exam_success(self, mock_calculate_score):
        # Certifica que a participação não existe antes de criá-la
        participation, created = ModelParticipation.objects.get_or_create(user=self.participant_user, exam=self.exam1)

        response = self.client.post(
            f"/api/exams/{self.exam1.id}/finish/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "Cálculo da pontuação iniciado")
        mock_calculate_score.assert_called_once_with(participation.id)

    def test_finish_exam_already_completed(self):
        # Marca a participação como finalizada, se ainda não existir
        participation, created = ModelParticipation.objects.get_or_create(
            user=self.participant_user,
            exam=self.exam1,
            defaults={"finished_at": make_aware(datetime(2024, 11, 29, 12, 0, 0))}
        )

        response = self.client.post(
            f"/api/exams/{self.exam1.id}/finish/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Prova ja finalizada")

    def test_finish_exam_no_participation(self):
        # Certifica-se de que nenhuma participação existe para esse usuário e prova
        ModelParticipation.objects.filter(user=self.participant_user, exam=self.exam1).delete()

        response = self.client.post(
            f"/api/exams/{self.exam1.id}/finish/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Participação nao encontrada")

    def test_check_progress_in_progress(self):
        # Cria uma participação que ainda está em progresso, se necessário
        ModelParticipation.objects.get_or_create(user=self.participant_user, exam=self.exam1)

        response = self.client.get(
            f"/api/exams/{self.exam1.id}/progress/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "in_progress")

    def test_check_progress_completed(self):
        # Cria uma participação finalizada com pontuação, se necessário
        participation, created = ModelParticipation.objects.get_or_create(
            user=self.participant_user,
            exam=self.exam1,
            defaults={
                "finished_at": make_aware(datetime(2024, 11, 29, 12, 0, 0)),
                "score": 85.0
            }
        )

        response = self.client.get(
            f"/api/exams/{self.exam1.id}/progress/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "completed")
        self.assertEqual(response.json()["score"], participation.score)

    def test_check_progress_no_participation(self):
        # Certifica-se de que nenhuma participação existe para esse usuário e prova
        ModelParticipation.objects.filter(user=self.participant_user, exam=self.exam1).delete()

        response = self.client.get(
            f"/api/exams/{self.exam1.id}/progress/",
            **self.participant_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Participação não encontrada")