from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models

class CustomUserManager(BaseUserManager):
    """
    Custom manager for User to use email as the unique identifier.
    """
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="api_customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="api_customuser_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
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
        exam_names = ", ".join(exam.name for exam in self.exams.all())
        return f"Exames: {exam_names if exam_names else 'Nenhum'} - {self.text[:50]}"


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
    


class ModelRanking(models.Model):
    exam = models.ForeignKey("ModelExam", on_delete=models.CASCADE, related_name="rankings")
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rankings")
    score = models.FloatField()
    position = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam", "participant")
        ordering = ["exam","position"]
    
    def __str__(self):
        return f"Ranking {self.exam.name} - {self.participant.username} - {self.score} - {self.position}"