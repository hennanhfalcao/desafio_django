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
   ```bash
    docker-compose build
    docker-compose up
   ```
3. **Crie um Superusuário (em outro terinal com o servidor rodando)**:
   ```bash
    python manage.py createsuperuser
   ```

4. **Autentique-se**: Envie uma requisição para a rota http://127.0.0.1:8000/api/token/ com as credenciais do superusuário.

5. **Documentação da API**: Acesse a documentação em http://127.0.0.1:8000/api/docs.
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
 - GET /api/users/{id}/: Detalhes de um usuário.
 - PATCH /api/users/{id}/: Atualização parcial de um usuário.
 - DELETE /api/users/{id}/: Exclusão de um usuário.
### Provas
 - POST /api/exams/: Criação de provas.
 - GET /api/exams/: Listagem de provas (com cache).
 - GET /api/exams/{id}/: Detalhes de uma prova.
 - PATCH /api/exams/patch/{id}/: Atualização parcial de uma prova.
 - PUT /api/exams/put/{id}/: Atualização completa de uma prova.
 - DELETE /api/exams/{id}/: Exclusão de uma prova.
 - POST /api/exams/{exam_id}/finish/: Finalizar uma prova.
 - GET /api/exams/{exam_id}/progress/: Progresso da correção de uma prova.
 - GET /api/ranking/{exam_id}/ranking/: Visualizar o ranking de uma prova.
### Questões
 - POST /api/questions/: Criação de questões.
 - GET /api/questions/: Listagem de questões (com cache).
 - GET /api/questions/{id}/: Detalhes de uma questão.
 - PATCH /api/questions/{id}/: Atualização parcial de uma questão.
 - DELETE /api/questions/{id}/: Exclusão de uma questão.
 - POST /api/questions/{question_id}/link-exam/{exam_id}/: Vincular uma questão a uma prova.
 - POST /api/questions/{question_id}/unlink-exam/{exam_id}/: Desvincular uma questão de uma prova.
### Respostas
 - POST /api/answers/: Criação de respostas.
 - GET /api/answers/: Listagem de respostas (com cache).
 - PATCH /api/answers/{id}/: Atualização de uma resposta.
### Participações
 - POST /api/exams/{exam_id}/participants/: Inscrição em uma prova.
 - GET /api/exams/{exam_id}/participants/: Listagem de participantes de uma prova.
 - DELETE /api/exams/{exam_id}/participants/{user_id}/: Remoção de um participante.
 - GET /api/exams/{exam_id}/participants/{user_id}/: Detalhes de uma participação.
 - PATCH /api/exams/{exam_id}/participants/{user_id}/: Atualização de uma participação.