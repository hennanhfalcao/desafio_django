from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from api.models import ModelQuestion, ModelExam, ModelUserProfile, ModelExamQuestion, ModelChoice


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

        # Criar alternativas
        self.choice1 = ModelChoice.objects.create(question=self.question1, text="Choice 1", is_correct=True)
        self.choice2 = ModelChoice.objects.create(question=self.question1, text="Choice 2", is_correct=False)

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
    # Testes de obtenção de questão individual
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

    # ============================
    # Testes de listagem de alternativas
    # ============================
    def test_list_choices_as_admin(self):
        response = self.client.get(f"/api/questions/{self.question1.id}/choices/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_list_choices_as_participant(self):
        response = self.client.get(f"/api/questions/{self.question1.id}/choices/", **self.participant_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_choices_for_nonexistent_question(self):
        response = self.client.get("/api/questions/9999/choices/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ============================
    # Testes de vinculação de alternativas
    # ============================
    def test_add_choice_as_admin(self):
        payload = {"question_id": self.question1.id, "text": "New Choice", "is_correct": False}
        response = self.client.post(f"/api/questions/{self.question1.id}/choices/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["text"], "New Choice")
        self.assertFalse(response.json()["is_correct"])

    def test_add_choice_exceeding_limit(self):
        ModelChoice.objects.create(question=self.question1, text="Choice 3", is_correct=False)
        ModelChoice.objects.create(question=self.question1, text="Choice 4", is_correct=False)

        payload = {"question_id": self.question1.id, "text": "Exceeding Choice", "is_correct": False}
        response = self.client.post(f"/api/questions/{self.question1.id}/choices/", payload, **self.admin_headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "A question can have at most 4 choices")

    # ============================
    # Testes de desvinculação de alternativas
    # ============================
    def test_remove_choice_as_admin(self):
        # Garanta que existam duas alternativas, uma correta e uma incorreta
        choice_to_remove = ModelChoice.objects.create(question=self.question1, text="Extra Choice", is_correct=False)

        # Certifique-se de que existe apenas uma alternativa correta
        correct_choice = ModelChoice.objects.get(question=self.question1, is_correct=True)

        # Tente remover a alternativa incorreta
        response = self.client.delete(
            f"/api/questions/{self.question1.id}/choices/{choice_to_remove.id}/",
            **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verifique se a alternativa foi removida
        self.assertFalse(ModelChoice.objects.filter(id=choice_to_remove.id).exists())

        # Verifique se a alternativa correta ainda existe
        self.assertTrue(ModelChoice.objects.filter(id=correct_choice.id).exists())

        # Verifique que a questão ainda tem pelo menos 2 alternativas
        self.assertGreaterEqual(ModelChoice.objects.filter(question=self.question1).count(), 2)

    def test_remove_choice_below_minimum(self):
        self.client.delete(f"/api/questions/{self.question1.id}/choices/{self.choice2.id}/", **self.admin_headers)

        response = self.client.delete(f"/api/questions/{self.question1.id}/choices/{self.choice1.id}/", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "A question must have at least 2 choices")