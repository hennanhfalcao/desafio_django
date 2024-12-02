from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q
from api.models import ModelQuestion, ModelExam, ModelChoice
from api.schemas import (
    QuestionSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    ErrorSchema,
)
from api.utils import is_authenticated, is_admin, order_queryset, paginate_queryset, clear_list_questions_cache, add_question_cache_key
from ninja.errors import HttpError
from django.core.cache import cache

router = Router(tags=["Questions"])

@router.post("/", response={201: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 422: ErrorSchema})
def create_question(request, payload: QuestionCreateSchema):
    """
    Cria uma questão e insere no banco de dados.
    Apenas administradores tem permissão para criar questões.
    Após criar uma questão, é possível linká-la a uma prova por meio da rota /api/questions/{question_id}/link-exam/{exam_id}/
    Para criar as questões insira as alternativas. Consulte os schemas para maiores detalhes.
    """

    is_authenticated(request)
    is_admin(request)

    question = ModelQuestion.objects.create(text=payload.text)
    for choice in payload.choices:
        ModelChoice.objects.create(
                                question=question, 
                                text=choice.text, 
                                is_correct=choice.is_correct
                                )
    clear_list_questions_cache()
    return 201, QuestionSchema.model_validate(question)

@router.get("/", response={200: list[QuestionSchema], 401: ErrorSchema, 403: ErrorSchema})
def list_questions(request, 
                query: str = None, 
                order_by: str = "-created_at", 
                page: int = 1, 
                page_size: int = 10
                ):
    """
    Lista todas as questões com busca, ordenação e paginação opcionais.
    É possível ordená-las por meio do campo created_at por meio da rota: /api/questions/?order_by=-created_at
    A páginação é feita por meio da rota: /api/questions/?page=2&page_size=10, em que os parâmetros page e page_size podem ser alterados.
    A busca por string é feita pelo campo text e pode ser testada acessando a rota: /api/questions/?query=
    """
    is_authenticated(request)
    is_admin(request)

    cache_key = f"list_questions:{query}:{order_by}:{page}:{page_size}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"Cache hit for key: {cache_key}")
        return cached_data

    try:
        questions = ModelQuestion.objects.all()
    except ModelQuestion.DoesNotExist:   
        raise HttpError(404, "Nenhuma questão encontrada") 
    if query:
        questions = questions.filter(Q(text__icontains=query))

    questions = order_queryset(questions, order_by)

    questions = paginate_queryset(questions, page, page_size)
    results = [QuestionSchema.model_validate(question) for question in questions]
    cache.set(cache_key, results, timeout=300)
    add_question_cache_key(cache_key)
    return results


@router.get("/{question_id}", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def get_question_details(request, question_id: int):
    """
    Recupera detalhes da questão por meio do ID.
    """
    is_authenticated(request)
    is_admin(request)
    question = get_object_or_404(ModelQuestion, id=question_id)
    return QuestionSchema.model_validate(question)

@router.patch("/patch/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def partial_update_question(request, question_id: int, payload: QuestionUpdateSchema):
    """
    Atualiza parcialmente uma questão por meio do seu ID.
    Se os IDS passados no payload não estiverem no banco de dados, retorna um erro.
    """
    is_authenticated(request)
    is_admin(request)

    question = get_object_or_404(ModelQuestion, id=question_id)
    if payload.text:
        question.text = payload.text
    
    if payload.exam_ids is not None:
        current_exam_ids = set(question.exams.values_list("id", flat=True))
        new_exams_ids = set(payload.exam_ids)

        exams_to_add = new_exams_ids - current_exam_ids
        if exams_to_add:
            exams_to_add_objects = ModelExam.objects.filter(id__in=exams_to_add)
            if len(exams_to_add_objects) != len(exams_to_add):
                missing_ids = set(payload.exam_ids) - set(exams_to_add_objects.values_list("id", flat=True))
                if missing_ids:
                    raise HttpError(404, f"Exames com os IDs {list(missing_ids)} não foram encontrados.")

            question.exams.add(*exams_to_add_objects)

        exams_to_remove = current_exam_ids - new_exams_ids
        if exams_to_remove:
            exams_to_remove_objects = ModelExam.objects.filter(id__in=exams_to_remove)
            question.exams.remove(*exams_to_remove_objects)

    if payload.choices is not None:
        question.choices.all().delete()

        for choice_data in payload.choices:
            ModelChoice.objects.create(
                question=question,
                text=choice_data.text,
                is_correct=choice_data.is_correct
            )

    question.save()       
    clear_list_questions_cache()
    return 200, QuestionSchema.model_validate(question)

@router.put("/put/{question_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema, 422: ErrorSchema})
def update_question(request, question_id: int, payload: QuestionUpdateSchema):
    """
    Atualiza completamente uma questão por meio do seu ID.
    Se os IDS das provas passados no payload não estiverem no banco de dados, retorna um erro.
    """
    is_authenticated(request)
    is_admin(request)

    question = get_object_or_404(ModelQuestion, id=question_id)

    if payload.text is None:
        raise HttpError(422, "O campo 'texto' é necessário para atualização completa")

    question.text = payload.text

    if payload.exam_ids is None:
        question.exams.clear()
    else:
        exams = ModelExam.objects.filter(id__in=payload.exam_ids)
        if len(exams) != len(payload.exam_ids):
            missing_ids = set(payload.exam_ids) - set(exams.values_list("id", flat=True))
            raise HttpError(404, f"Exames com os IDs {list(missing_ids)} não foram encontrados.")
        question.exams.set(exams)


    if payload.choices is None:
        question.choices.all().delete()
    else:
        question.choices.all().delete()

        for choice_data in payload.choices:
            ModelChoice.objects.create(
                question=question,
                text=choice_data.text,
                is_correct=choice_data.is_correct
            )

    question.save()
    clear_list_questions_cache()
    return 200, QuestionSchema.model_validate(question)

@router.delete("/delete/{question_id}/", response={204: None, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def delete_question(request, question_id: int):
    """
    Deleta uma questão pelo ID.
    Apenas administradores podem deletar questões.
    """
    is_authenticated(request)
    is_admin(request)
    question = get_object_or_404(ModelQuestion, id=question_id)
    question.delete()
    clear_list_questions_cache()
    return 204, None


@router.post("/{question_id}/link-exam/{exam_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def link_question_to_exam(request, question_id: int, exam_id: int):
    """
    Vincula uma questão a uma prova.
    Apenas administradores tem permissão
    O retorno é a questão com o campo de provas relacionadas atualizado.
    """
    is_authenticated(request)
    is_admin(request)

    question = get_object_or_404(ModelQuestion, id=question_id)
    exam = get_object_or_404(ModelExam, id=exam_id)
    question.exams.add(exam)
    question.save()
    clear_list_questions_cache()
    return 200, QuestionSchema.model_validate(question)

@router.delete("/{question_id}/unlink-exam/{exam_id}/", response={200: QuestionSchema, 401: ErrorSchema, 403: ErrorSchema, 404: ErrorSchema})
def unlink_question_from_exam(request, question_id: int, exam_id: int):
    """
    Desvincula uma questão de uma prova.
    Apenas administradores tem permissão.
    O retorno é a questão com o campo de provas relacionadas atualizado.
    """
    is_authenticated(request)
    is_admin(request)

    question = get_object_or_404(ModelQuestion, id=question_id)
    exam = get_object_or_404(ModelExam, id=exam_id)
    question.exams.remove(exam)
    question.save()
    clear_list_questions_cache()
    return QuestionSchema.model_validate(question)