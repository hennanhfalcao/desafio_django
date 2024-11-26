from ninja import Schema
from pydantic import EmailStr
from datetime import datetime
from typing import List
from pydantic import BaseModel
from typing import Optional

class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
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
    email: Optional[str]
    is_admin: Optional[bool]
    is_participant: Optional[bool]

    class Config:
        orm_mode = True
                
class ExamCreateSchema(Schema):
    name: str

class ExamSchema(Schema):
    id: int
    name: str
    created_by_id: int
    created_at: datetime

class QuestionCreateSchema(Schema):
    exam_id: int
    text: str

class QuestionSchema(Schema):
    id: int
    exam_id: int
    text: str
    created_at: datetime

class ChoicesCreateSchema(Schema):
    question_id: int
    text: str
    is_correct: bool

class ChoicesSchema(Schema):
    id: int
    question_id: int
    text: str
    is_correct: bool

class ParticipationCreateSchema(Schema):
    exam_id: int

class ParticipationSchema(Schema):
    id: int
    user: int
    exam: int
    started_at: datetime
    finished_at: datetime = None
    score: float

class AnswerCreateSchema(Schema):
    participation_id: int
    question_id: int
    choice_id: int

class AnswerSchema(Schema):
    id: int
    participation_id: int
    question_id: int
    choice_id: int
    answered_at: datetime    