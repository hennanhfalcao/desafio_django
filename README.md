# Web Service RESTful com Django Ninja para Gerenciamento de provas

## Visão Geral

Desenvolvimento de um Web Service RESTful para o gerenciamento de provas com questões de múltipla escolha. A aplicação suporta a comunicação com aplicativos móveis e web e inclui funcionalidades como gerenciamento de usuários, provas, questões, respostas e rankings de participantes.

---

## Funcionalidades

- **Gerenciamento de Usuários**: Criação, edição, exclusão, listagem e exibição individual de usuários.
- **Gerenciamento de Provas**: Criação, edição, exclusão, listagem e exibição individual de provas.
- **Gerenciamento de Questões**: Criação, edição, exclusão, listagem e exibição individual de questões.
- **Gerenciamento de Escolhas**: Criação, edição, exclusão, listagem e exibição individual de escolhas.
- **Gerenciamento de Participantes**: Inscrição em provas e acompanhamento.
- **Sistema de Respostas**: Envio e edição de respostas por participantes.
- **Correção Automática**: Correção assíncrona das respostas dos participantes.
- **Rankings**: Cálculo e disponibilização de rankings de candidatos por prova.
- **Autenticação**: Sistema de autenticação JWT.
- **Cache**: Implementação de cache para endpoints de listagem.
- **Testes Unitários**: Cobertura de testes para todas as operações principais.

---

## Tecnologias Utilizadas

- **Linguagem**: Python 3.10
- **Framework**: Django e Django Ninja
- **Cache**: Redis
- **Task Queue**: Celery + Celery Beat
- **Banco de Dados**: SQLite (Desenvolvimento)
- **Gerenciador de Dependências**: Poetry
- **Containerização**: Docker e Docker Compose

---

## Instruções para Executar Localmente

### Pré-requisitos

1. Ter o **Docker** e **Docker Compose** instalados.
2. Ter o **Python 3.10** instalado para comandos fora do Docker (opcional).

### Passo a Passo

1. **Clone o Repositório**:
   ```bash
    git clone https://github.com/hennanhfalcao/desafio_django.git
    cd desafio_django
   ```
2. **Execute a Aplicação com Docker Compose**:
   
   O Docker Desktop deve estar em execução.
   ```bash
    docker-compose build
    docker-compose up
   ```
3. **Crie um Superusuário (em outro terminal com o servidor rodando, dentro do container desafio_django-web-1)**:
   ```bash
    python manage.py createsuperuser
   ```

4. **Autentique-se**: Envie uma requisição para a rota http://127.0.0.1:8000/api/token/ou http://localhost:8000/api/token/ com as credenciais do superusuário.

5. **Documentação da API**: Acesse a documentação em http://127.0.0.1:8000/api/docs ou http://localhost:8000/api/docs.
 - A documentação conta com exemplos de requisições e com os esquemas de serialização de dados.

### Testes
Para rodar os testes unitários:
   ```bash
    python manage.py test api.tests
   ```

## Rotas da API
### Usuários
 - POST /api/users/: Criação de usuários.
 - GET /api/users/: Listagem de usuários.
 - GET /api/users/{user_id}/: Detalhes de um usuário.
 - PATCH /api/users/{user_id}/: Atualização parcial de um usuário.
 - DELETE /api/users/{user_id}/: Exclusão de um usuário.
### Provas
 - POST /api/exams/: Criação de provas.
 - GET /api/exams/: Listagem de provas (com cache).
 - GET /api/exams/{exam_id}/: Detalhes de uma prova.
 - PATCH /api/exams/{exam_id}/: Atualização parcial de uma prova.
 - PUT /api/exams/{exam_id}/: Atualização completa de uma prova.
 - DELETE /api/exams/{exam_id}/: Exclusão de uma prova.
 - GET /api/exams/{exam_id}/participants/: Lista participantes de uma prova.
 - POST /api/exams/{exam_id}/participants/: Insere um pasticipante em uma prova.
 - DELETE /api/exams/{exam_id}/participants/{user_id}/: Deleta uma participação.
 - GET /api/exams/{exam_id}/participants/{user_id}/: Exibe detalhes de uma participação.
 - PATCH /api/exams/{exam_id}/participants/{user_id}: Atualização parcial de uma participação.
 - POST /api/exams/{exam_id}/conclusions/: Finaliza a participação em uma prova, está relacionada ao usuário que está logado.
 - GET /api/exams/{exam_id}/progresses/: Consulta o progresso do processamento de uma correção, se tiver acabado, exibe o score.
### Questões
 - POST /api/questions/: Criação de questões.
 - GET /api/questions/: Listagem de questões (com cache).
 - GET /api/questions/{question_id}/: Detalhes de uma questão.
 - PATCH /api/questions/{question_id}/: Atualização parcial de uma questão.
 - PUT /api/questions/{question_id}/: Atualização completa de uma questão.
 - DELETE /api/questions/{question_id}/: Exclusão de uma questão.
 - POST /api/questions/{question_id}/exams/{exam_id}/: Vincular uma questão a uma prova.
 - DELETE /api/questions/{question_id}/exams/{exam_id}/: Desvincular uma questão de uma prova.
### Respostas
 - POST /api/answers/: Criação de respostas.
 - GET /api/answers/participants/{participation_id}/: Listagem de respostas (com cache).
 - GET /api/answers/{answer_id}/: Detalhes de uma resposta.
 - PATCH /api/answers/{answer_id}/: Atualização de uma resposta.
 - DELETE /api/answers/{asnwer_id}/: Deleção de uma resposta.
### Ranking
 - GET /api/rankings/exams/{exam_id}: Obtém o ranking para uma determinada prova

## Cenários demonstrativos

**Siga o fluxo de execução**:
1. Crie um superusuário no shell do Django
2. Autentique-o para receber o token
3. Crie usuários participantes e administradores
4. Crie provas
5. Crie questões (Entenda questão como: enunciado e alternativas, no ato do cadastro da questão, indique a alternativa correta.)
6. Associe questões a provas
7. Crie partipações de usuários em provas
8. Responda questões(logando como participante, visto que apenas participantes de uma prova podem responder suas questões.)
9. Conclua a participação em uma prova para calcular sua pontuação assíncronamente
10. Consulte o resultado e o ranking


A seguir 
### Criar usuário
**Método:** POST  
**URL:** http://localhost:8000/api/users/  

**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Corpo:**
```json
{
  "username": "Hennan",
  "password": "123",
  "email": "hennan@gmail.com",
  "is_admin": true,
  "is_participant": true
}
```
Para fins de teste o usuário administrador foi setado (você pode fazer isso utilizando o método PATCH) como participante.

**Resposta esperada**:
```json
{
	"id": 1,
	"username": "Hennan",
	"email": "hennan@gmail.com",
	"is_admin": true,
	"is_participant": true
}
```


### Criar Questão

**Método:** POST  
**URL:** http://localhost:8000/api/questions/  

**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Corpo:**

```json
{
  "text" : "Teste 3",
	"choices": [
    {
      "text": "alternativa1",
      "is_correct": true
    },
		{
      "text": "alternativa2",
      "is_correct": false
    },
		{
      "text": "alternativa3",
      "is_correct": false
    }
  ]
}
```

**Resposta esperada**:

```json
{
	"id": 3,
	"text": "Teste 3",
	"created_at": "2024-12-03T21:33:21.881Z",
	"choices": [
		{
			"id": 13,
			"text": "alternativa1",
			"is_correct": true
		},
		{
			"id": 14,
			"text": "alternativa2",
			"is_correct": false
		},
		{
			"id": 15,
			"text": "alternativa3",
			"is_correct": false
		}
	],
	"exam_ids": []
}
```

### Criar prova

**Método:** POST  
**URL:** http://localhost:8000/api/exams/  

**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Corpo:**

```json
{
  "name":"Prova 1 Teste"
}
```

**Resposta esperada**:

```json
{
	"id": 1,
	"name": "Prova 1 Teste",
	"created_by": {
		"id": 1,
		"username": "Hennan",
		"email": "hennan@gmail.com",
		"is_admin": true,
		"is_participant": true
	},
	"created_at": "2024-12-04T01:41:07.711Z",
	"questions": []
}
```
### Linke uma questão ou várias questões a uma prova.

**Método:** POST  
**URL:** http://localhost:8000/api/questions/1/exams/1/

**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Resposta esperada**:

```json
{
	"id": 1,
	"text": "Teste 3",
	"created_at": "2024-12-04T01:40:56.303Z",
	"choices": [
		{
			"id": 1,
			"text": "alternativa1",
			"is_correct": true
		},
		{
			"id": 2,
			"text": "alternativa2",
			"is_correct": false
		},
		{
			"id": 3,
			"text": "alternativa3",
			"is_correct": false
		}
	],
	"exam_ids": [
		1
	]
}
```

### Criar participação em prova

**Método:** POST  
**URL:** http://localhost:8000/api/exams/<exam_id>/participants/ 

**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Corpo:**

```json
{
  "user_id": 1,
	"exam_id": 1
}
```

**Resposta esperada**:

```json
{
	"id": 1,
	"user": {
		"id": 1,
		"username": "Hennan",
		"email": "hennan@gmail.com",
		"is_admin": true,
		"is_participant": true
	},
	"exam": {
		"id": 1,
		"name": "Prova 1 Teste",
		"created_by": {
			"id": 1,
			"username": "Hennan",
			"email": "hennan@gmail.com",
			"is_admin": true,
			"is_participant": true
		},
		"created_at": "2024-12-04T01:41:07.711Z",
		"questions": [
			{
				"id": 1,
				"text": "Teste 3",
				"created_at": "2024-12-04T01:40:56.303Z",
				"choices": [
					{
						"id": 1,
						"text": "alternativa1",
						"is_correct": true
					},
					{
						"id": 2,
						"text": "alternativa2",
						"is_correct": false
					},
					{
						"id": 3,
						"text": "alternativa3",
						"is_correct": false
					}
				],
				"exam_ids": [
					1
				]
			}
		]
	},
	"started_at": "2024-12-04T01:42:11.293Z",
	"finished_at": null,
	"score": 0.0
}
```

### Responder a uma questão

**Método:** POST  
**URL:** http://localhost:8000/api/answers/

**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Corpo:**

```json
{
	"participation_id": 1,
	"question_id": 1,
	"choice_id": 1
}
```

**Resposta esperada**:

```json
{
	"id": 1,
	"participation": {
		"id": 1,
		"user": {
			"id": 1,
			"username": "Hennan",
			"email": "hennan@gmail.com",
			"is_admin": true,
			"is_participant": true
		},
		"exam": {
			"id": 1,
			"name": "Prova 1 Teste",
			"created_by": {
				"id": 1,
				"username": "Hennan",
				"email": "hennan@gmail.com",
				"is_admin": true,
				"is_participant": true
			},
			"created_at": "2024-12-04T01:41:07.711Z",
			"questions": [
				{
					"id": 1,
					"text": "Teste 3",
					"created_at": "2024-12-04T01:40:56.303Z",
					"choices": [
						{
							"id": 1,
							"text": "alternativa1",
							"is_correct": true
						},
						{
							"id": 2,
							"text": "alternativa2",
							"is_correct": false
						},
						{
							"id": 3,
							"text": "alternativa3",
							"is_correct": false
						}
					],
					"exam_ids": [
						1
					]
				}
			]
		},
		"started_at": "2024-12-04T01:42:11.293Z",
		"finished_at": null,
		"score": 0.0
	},
	"question": {
		"id": 1,
		"text": "Teste 3",
		"created_at": "2024-12-04T01:40:56.303Z",
		"choices": [
			{
				"id": 1,
				"text": "alternativa1",
				"is_correct": true
			},
			{
				"id": 2,
				"text": "alternativa2",
				"is_correct": false
			},
			{
				"id": 3,
				"text": "alternativa3",
				"is_correct": false
			}
		],
		"exam_ids": [
			1
		]
	},
	"choice": {
		"id": 1,
		"text": "alternativa1",
		"is_correct": true
	},
	"answered_at": "2024-12-04T01:42:57.783Z"
}
```

### Finalize a prova

**Método:** POST  
**URL:** http://127.0.0.1:8000/api/exams/1/conclusions/


**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Resposta esperada**:

```json
{
	"detail": "Cálculo da pontuação iniciado"
}
```

A pontuação será calculada assícronamente por meio do Celery

### Consulte o resultado

**Método:** GET  
**URL:** http://127.0.0.1:8000/api/exams/1/progresses/


**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Resposta esperada**:

```json
{
	"status": "completed",
	"score": 100.0
}
```
### Consulte o ranking
**Método:** GET  
**URL:** http://127.0.0.1:8000/api/rankings/exams/1/


**Cabeçalhos:**
Content-Type: application/json  
Authorization: Bearer <seu_token_aqui>

**Resposta esperada**:

```json
[
	{
		"exam_id": 1,
		"participant_id": 1,
		"participant_username": "Hennan",
		"score": 100.0,
		"position": 1
	}
]
```
### Consulte a documentação para mais detalhes dos esquemas de serialização.