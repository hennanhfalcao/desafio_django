from ninja import Schema
from pydantic import EmailStr
from datetime import datetime
from typing import List

class UserCreateSchema(Schema):
    username: str
    password: str
    email: EmailStr
    is_admin: bool = False
    is_participant: bool = True

class UserSchema(Schema):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    is_participant: bool

class ExamCreateSchema(Schema):
    name: str

class ExamSchema(Schema):
    id: int
    name: str
    created_by_id: int
    created_at: str

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