from django.contrib.auth.models import User
from django.db import models


# Modelo de Perfil de Usuário
class ModelUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_admin = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - Admin: {self.is_admin} - Participant: {self.is_participant}"


# Modelo de Provas
class ModelExam(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_exams")
    participants = models.ManyToManyField(User, through="ModelParticipation", related_name="exams")
    questions = models.ManyToManyField('ModelQuestion', related_name="exams")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Modelo de Participação com dados adicionais
class ModelParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participations")
    exam = models.ForeignKey(ModelExam, on_delete=models.CASCADE, related_name="participations")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.exam.name}"


# Modelo de Questões
class ModelQuestion(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam.name} - {self.text[:50]}"


# Modelo de Escolhas
class ModelChoice(models.Model):
    question = models.ForeignKey(ModelQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:50]} - {self.text}"


# Modelo de Respostas
class ModelAnswer(models.Model):
    participation = models.ForeignKey(ModelParticipation, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(ModelQuestion, on_delete=models.CASCADE, related_name="answers")
    choice = models.ForeignKey(ModelChoice, on_delete=models.CASCADE, related_name="answers")
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participation.user.username} - {self.question.text[:50]} - {self.choice.text}"