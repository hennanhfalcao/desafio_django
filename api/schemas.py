from ninja import Schema
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
    def from_orm(cls, obj):
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


# Choice Schemas
class ChoicesSchema(BaseModel):
    id: int
    question_id: int
    text: str
    is_correct: bool

    class Config:
        orm_mode = True


class ChoicesCreateSchema(BaseModel):
    question_id: int
    text: str
    is_correct: bool


class ChoicesUpdateSchema(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = None

    class Config:
        orm_mode = True


# Question Schemas
class QuestionSchema(BaseModel):
    id: int
    text: str
    created_at: datetime
    exams: List[int]
    choices: List[dict]  # Lista de alternativas associadas

    class Config:
        orm_mode = True


class QuestionCreateSchema(BaseModel):
    text: str
    exams: Optional[List[int]] = None

    class Config:
        orm_mode = True


class QuestionUpdateSchema(BaseModel):
    text: Optional[str] = None
    exams: Optional[List[int]] = None

    class Config:
        orm_mode = True


# Exam Schemas
class ExamSchema(BaseModel):
    id: int
    name: str
    created_by: UserSchema
    created_at: datetime
    participants: List["ExamParticipantSchema"]
    questions: List["ExamQuestionSchema"]

    class Config:
        orm_mode = True


class ExamCreateSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True


class ExamUpdateSchema(BaseModel):
    name: Optional[str]

    class Config:
        orm_mode = True


# Intermediate Model Schemas
class ExamParticipantSchema(BaseModel):
    exam_id: int
    user_id: int
    added_at: datetime

    class Config:
        orm_mode = True


class ExamParticipantCreateSchema(BaseModel):
    exam_id: int
    user_id: int

    class Config:
        orm_mode = True


class ExamQuestionSchema(BaseModel):
    exam_id: int
    question: QuestionSchema  # QuestionSchema completo

    class Config:
        orm_mode = True


class ExamQuestionCreateSchema(BaseModel):
    exam_id: int
    question_id: int

    class Config:
        orm_mode = True


# Participation Schemas
class ParticipationSchema(BaseModel):
    id: int
    user: UserSchema
    exam: ExamSchema
    started_at: datetime
    finished_at: Optional[datetime]
    score: float

    class Config:
        orm_mode = True


class ParticipationCreateSchema(BaseModel):
    exam_id: int


# Answer Schemas
class AnswerSchema(BaseModel):
    id: int
    participation: ParticipationSchema
    question: QuestionSchema
    choice: ChoicesSchema
    correct_choice: Optional[ChoicesSchema]  # Adicionado para mostrar a resposta correta
    answered_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            participation=ParticipationSchema.from_orm(obj.participation),
            question=QuestionSchema.from_orm(obj.question),
            choice=ChoicesSchema.from_orm(obj.choice),
            correct_choice=ChoicesSchema.from_orm(obj.question.get_correct_choice()),
            answered_at=obj.answered_at,
        )

    class Config:
        orm_mode = True


class AnswerCreateSchema(BaseModel):
    participation_id: int
    question_id: int
    choice_id: int


# Error Schema
class ErrorSchema(BaseModel):
    detail: str