from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelUserProfile, ModelExam, ModelQuestion, ModelExamParticipant, ModelExamQuestion


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

        # Criação de prova
        self.exam = ModelExam.objects.create(name="Test Exam", created_by=self.admin_user)

        # Criação de questões
        self.question1 = ModelQuestion.objects.create(text="Question 1")
        self.question2 = ModelQuestion.objects.create(text="Another Question")
        self.question3 = ModelQuestion.objects.create(text="Sample Question")

        # Vincula questões à prova
        ModelExamQuestion.objects.create(exam=self.exam, question=self.question1)
        ModelExamQuestion.objects.create(exam=self.exam, question=self.question2)
        ModelExamQuestion.objects.create(exam=self.exam, question=self.question3)

        # Inscreve múltiplos participantes na prova com verificação de duplicidade
        for i in range(1, 6):
            user = User.objects.create_user(
                username=f"participant{i}",
                password=f"participant{i}123",
                email=f"participant{i}@example.com"
            )
            ModelUserProfile.objects.create(
                user=user,
                is_admin=False,
                is_participant=True
            )
            if not ModelExamParticipant.objects.filter(exam=self.exam, user=user).exists():
                ModelExamParticipant.objects.create(exam=self.exam, user=user)

        # Inscrição do participante principal
        if not ModelExamParticipant.objects.filter(exam=self.exam, user=self.participant_user).exists():
            ModelExamParticipant.objects.create(exam=self.exam, user=self.participant_user)

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
    # Testes de provas (Exams)
    # ============================

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

    def test_list_exams_as_admin(self):
        response = self.client.get("/api/exams/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()) > 0)

    def test_list_exams_as_participant(self):
        response = self.client.get("/api/exams/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exams = response.json()
        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0]["id"], self.exam.id)

    def test_delete_exam_as_admin(self):
        response = self.client.delete(f"/api/exams/{self.exam.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_exam_as_participant(self):
        response = self.client.delete(f"/api/exams/{self.exam.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Permission denied")

    # ============================
    # Testes de participantes
    # ============================

    def test_list_participants_as_admin(self):
        response = self.client.get(f"/api/exams/{self.exam.id}/participants/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 6)  # Ajustar para o valor real
        self.assertIn("user_id", response.json()[0])
        self.assertEqual(response.json()[0]["exam_id"], self.exam.id)

    def test_add_participant_as_admin(self):
        payload = {"exam_id": self.exam.id, "user_id": self.participant_user.id}
        response = self.client.post(
            f"/api/exams/{self.exam.id}/participants/",
            payload,
            **self.admin_headers,
            format="json",
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertEqual(
                response.json()["detail"], 
                "User is already a participant in this exam"
            )
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(
                ModelExamParticipant.objects.filter(
                    exam=self.exam, 
                    user=self.participant_user
                ).exists()
            )

    def test_add_participant_as_participant(self):
        payload = {"exam_id": self.exam.id, "user_id": self.participant_user.id}
        response = self.client.post(
            f"/api/exams/{self.exam.id}/participants/",
            payload,
            **self.participant_headers,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_participant_as_admin(self):
        participant = ModelExamParticipant.objects.filter(exam=self.exam).first()
        response = self.client.delete(
            f"/api/exams/{self.exam.id}/participants/{participant.user_id}/",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_participants_with_search(self):
        response = self.client.get(
            f"/api/exams/{self.exam.id}/participants/?query=participant3",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["user_id"], User.objects.get(username="participant3").id)

    def test_list_participants_with_ordering(self):
        response = self.client.get(
            f"/api/exams/{self.exam.id}/participants/?order_by=user__email",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        participants = response.json()
        user_emails = [User.objects.get(id=p["user_id"]).email for p in participants]
        self.assertTrue(all(user_emails[i] <= user_emails[i + 1] for i in range(len(user_emails) - 1)))

    def test_list_participants_with_pagination(self):
        response = self.client.get(
            f"/api/exams/{self.exam.id}/participants/?page=1&page_size=2",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    # ============================
    # Testes de questões
    # ============================

    def test_list_questions_as_admin(self):
        response = self.client.get(f"/api/exams/{self.exam.id}/questions/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)
        self.assertIn("question_id", response.json()[0])
        self.assertEqual(response.json()[0]["exam_id"], self.exam.id)

    def test_list_questions_as_participant(self):
        response = self.client.get(f"/api/exams/{self.exam.id}/questions/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)
        question_ids = [q["question_id"] for q in response.json()]
        self.assertIn(self.question1.id, question_ids)
        self.assertIn(self.question2.id, question_ids)
        self.assertIn(self.question3.id, question_ids)

    def test_add_question_as_admin(self):
        question = ModelQuestion.objects.create(text="Sample Question")
        payload = {"exam_id": self.exam.id, "question_id": question.id}
        response = self.client.post(
            f"/api/exams/{self.exam.id}/questions/",
            payload,
            **self.admin_headers,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_question_as_participant(self):
        question = ModelQuestion.objects.create(text="Sample Question")
        payload = {"exam_id": self.exam.id, "question_id": question.id}
        response = self.client.post(
            f"/api/exams/{self.exam.id}/questions/",
            payload,
            **self.participant_headers,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_question_as_admin(self):
        response = self.client.delete(f"/api/exams/{self.exam.id}/questions/{self.question1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_remove_question_as_participant(self):
        response = self.client.delete(f"/api/exams/{self.exam.id}/questions/{self.question1.id}/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_questions_with_search(self):
        response = self.client.get(
            f"/api/exams/{self.exam.id}/questions/?query=Another",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        question = ModelQuestion.objects.get(id=response.json()[0]["question_id"])
        self.assertEqual(question.text, "Another Question")

    def test_list_questions_with_ordering(self):
        response = self.client.get(
            f"/api/exams/{self.exam.id}/questions/?order_by=question__text",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = response.json()
        question_texts = [ModelQuestion.objects.get(id=q["question_id"]).text for q in questions]
        self.assertTrue(all(question_texts[i] <= question_texts[i + 1] for i in range(len(question_texts) - 1)))

    def test_list_questions_with_pagination(self):
        response = self.client.get(
            f"/api/exams/{self.exam.id}/questions/?page=1&page_size=2",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)