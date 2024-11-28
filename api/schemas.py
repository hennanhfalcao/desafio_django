from ninja import Schema
from pydantic import EmailStr
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from api.models import ModelExamQuestion


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

class ExamCreateSchema(BaseModel):
    name: str

class ExamSchema(BaseModel):
    id: int
    name: str
    created_by_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
class ExamUpdateSchema(BaseModel):
    name: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True
class ExamParticipantCreateSchema(BaseModel):
    exam_id: int
    user_id: int

class ExamParticipantSchema(BaseModel):
    exam_id: int
    user_id: int
    added_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
class ExamQuestionCreateSchema(BaseModel):
    exam_id: int
    question_id: int

    class Config:
        orm_mode = True
        from_attributes = True
class ExamQuestionSchema(BaseModel):
    exam_id: int
    question_id: int
    added_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class QuestionCreateSchema(BaseModel):
    text: str
    exams: Optional[List[int]] = None

    class Config:
        orm_mode = True
        from_attributes = True

class QuestionSchema(BaseModel):
    id: int
    text: str
    created_at: datetime
    exams: List[int]  # Campo para os IDs dos exames

    class Config:
        orm_mode = True
        from_attributes = True

class QuestionUpdateSchema(BaseModel):
    text: Optional[str] = None
    exams: Optional[List[int]] = None

    class Config:
        orm_mode = True
        from_attributes = True
class ChoicesCreateSchema(BaseModel):
    question_id: int
    text: str
    is_correct: bool

class ChoicesSchema(BaseModel):
    id: int
    question_id: int
    text: str
    is_correct: bool

    class Config:
        orm_mode = True
        from_attributes = True
class ParticipationCreateSchema(BaseModel):
    exam_id: int

class ParticipationSchema(BaseModel):
    id: int
    user: int
    exam: int
    started_at: datetime
    finished_at: Optional[datetime]
    score: float

    class Config:
        orm_mode = True
        from_attributes = True
class AnswerCreateSchema(BaseModel):
    participation_id: int
    question_id: int
    choice_id: int

class AnswerSchema(BaseModel):
    id: int
    participation_id: int
    question_id: int
    choice_id: int
    answered_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
class ErrorSchema(BaseModel):
    detail: str