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
            is_admin=obj.is_admin,
            is_participant=obj.is_participant,
        )

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
    is_admin: Optional[bool]
    is_participant: Optional[bool]

    class Config:
        from_attributes = True

# Exam Schemas

class ExamUpdateSchema(BaseModel):
    name: Optional[str]

    class Config:
        from_attributes=True


class ExamSchema(BaseModel):
    id: int
    name: str
    created_by: UserSchema
    created_at: datetime
    questions: Optional[List["QuestionSchema"]] # Relacionamento muitos-para-muitos

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

class ParticipationCreateSchema(BaseModel):
    user_id: int
    exam_id: int

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

class ParticipationUpdateSchema(BaseModel):
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    score: Optional[float] = None


# Question Schemas
class QuestionSchema(BaseModel):
    id: int
    text: str
    created_at: datetime
    choices: List["ChoiceSchema"]
    exam_ids: List[int]

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            text=obj.text,
            created_at=obj.created_at,
            choices=[ChoiceSchema.model_validate(c) for c in obj.choices.all()],
            exam_ids=list(obj.exams.values_list("id", flat=True)),
        )


class QuestionCreateSchema(BaseModel):
    text: str
    choices: List["ChoiceCreateSchema"]

class QuestionUpdateSchema(BaseModel):
    text: Optional[str] = None
    exam_ids: Optional[List[int]] = None 
    choices: Optional[List["ChoiceUpdateSchema"]] = None 
    

# Choice Schemas
class ChoiceSchema(BaseModel):
    id: int
    text: str
    is_correct: bool


    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            text=obj.text,
            is_correct=obj.is_correct,
        )


class ChoiceCreateSchema(BaseModel):
    text: str
    is_correct: bool

class ChoiceUpdateSchema(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = None


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


class AnswerUpdateSchema(BaseModel):
    participation_id: Optional[int] = None
    question_id: Optional[int] = None
    choice_id: Optional[int] = None

class ErrorSchema(BaseModel):
    detail: str

class RankingSchema(BaseModel):
    exam_id: int
    participant_id: int
    participant_username: str
    score: float
    position: int