from django.contrib.auth.models import User
from django.db import models


class ModelUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_admin = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - Admin: {self.is_admin} - Participant: {self.is_participant}"


class ModelExam(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_exams")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ModelQuestion(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

    def get_correct_choice(self):
        """Retorna a alternativa correta para a questão."""
        return self.choices.filter(is_correct=True).first()


class ModelChoice(models.Model):
    question = models.ForeignKey(ModelQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question"],
                condition=models.Q(is_correct=True),
                name="unique_correct_choice_per_question"
            )
        ]

    def __str__(self):
        return f"{self.question.text[:50]} - {self.text}"


class ModelParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participations")
    exam = models.ForeignKey(ModelExam, on_delete=models.CASCADE, related_name="participations")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.exam.name}"


class ModelAnswer(models.Model):
    participation = models.ForeignKey(ModelParticipation, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(ModelQuestion, on_delete=models.CASCADE, related_name="answers")
    choice = models.ForeignKey(ModelChoice, on_delete=models.CASCADE, related_name="answers")
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("participation", "question")

    def __str__(self):
        return f"{self.participation.user.username} - {self.question.text[:50]} - {self.choice.text}"


class ModelExamParticipant(models.Model):
    exam = models.ForeignKey(ModelExam, on_delete=models.CASCADE, related_name="exam_participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_exams")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam", "user")

    def __str__(self):
        return f"Exam: {self.exam.name}, Participant: {self.user.username}"


class ModelExamQuestion(models.Model):
    exam = models.ForeignKey(ModelExam, on_delete=models.CASCADE, related_name="exam_questions")
    question = models.ForeignKey(ModelQuestion, on_delete=models.CASCADE, related_name="question_exams")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam", "question")

    def __str__(self):
        return f"Exam: {self.exam.name}, Question: {self.question.text[:50]}"