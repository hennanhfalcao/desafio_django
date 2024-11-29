from pydantic import EmailStr
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# User Schemas
class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    is_admin: bool
    is_participant: bool


class UserSchema(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_admin: bool
    is_participant: bool

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            username=obj.username,
            email=obj.email,
            is_admin=obj.profile.is_admin,
            is_participant=obj.profile.is_participant,
        )

    class Config:
        orm_mode = True


class UserUpdateSchema(BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
    is_admin: Optional[bool]
    is_participant: Optional[bool]

    class Config:
        orm_mode = True

# Exam Schemas
class ExamSchema(BaseModel):
    id: int
    name: str
    created_by: UserSchema
    created_at: datetime
    questions: List["QuestionSchema"]  # Relacionamento muitos-para-muitos

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            created_by=UserSchema.model_validate(obj.created_by),
            created_at=obj.created_at,
            questions=[QuestionSchema.model_validate(q) for q in obj.questions.all()],
        )


class ExamCreateSchema(BaseModel):
    name: str


# Participation Schemas
class ParticipationSchema(BaseModel):
    id: int
    user: UserSchema
    exam: ExamSchema
    started_at: datetime
    finished_at: Optional[datetime]
    score: float

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            user=UserSchema.model_validate(obj.user),
            exam=ExamSchema.model_validate(obj.exam),
            started_at=obj.started_at,
            finished_at=obj.finished_at,
            score=obj.score,
        )


# Question Schemas
class QuestionSchema(BaseModel):
    id: int
    text: str
    created_at: datetime
    exams: List[ExamSchema]  # Relacionamento muitos-para-muitos

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            text=obj.text,
            created_at=obj.created_at,
            exams=[ExamSchema.model_validate(e) for e in obj.exams.all()],
        )


class QuestionCreateSchema(BaseModel):
    text: str
    exam_id: int  # ID do exame ao qual a questão pertence


# Choice Schemas
class ChoiceSchema(BaseModel):
    id: int
    text: str
    is_correct: bool
    question_id: int

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            text=obj.text,
            is_correct=obj.is_correct,
            question_id=obj.question.id,
        )


class ChoiceCreateSchema(BaseModel):
    question_id: int
    text: str
    is_correct: bool


# Answer Schemas
class AnswerSchema(BaseModel):
    id: int
    participation: ParticipationSchema
    question: QuestionSchema
    choice: ChoiceSchema
    answered_at: datetime

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            participation=ParticipationSchema.model_validate(obj.participation),
            question=QuestionSchema.model_validate(obj.question),
            choice=ChoiceSchema.model_validate(obj.choice),
            answered_at=obj.answered_at,
        )


class AnswerCreateSchema(BaseModel):
    participation_id: int
    question_id: int
    choice_id: int


class ErrorSchema(BaseModel):
    detail: str    