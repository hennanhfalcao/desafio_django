# desafio_django
Desenvolvimento de uma Web Service RESTful para gerenciamento de provas com questões de múltiplas escolhas. 

## Para executar o projeto via Docker, todos os comandos necessários para a inicialização da aplicação no servidor serão executados, incluindo instalação de dependências via poetry. Basta executar os comandos:
```python
docker-compose build
docker-compose up
```

## Crie um superusuário em outro terminal com o servidor rodando
`python manage.py createsuperuser`

## Autentique-o via Insomnia ou Postman passando username e senha no corpo da requisição feita para a rota http://127.0.0.1:8000/api/token/

## Cenário Demonstrativo
### Simulação de uso da aplicação:
**Usuários**:

Crie um usuário administrador e usuários participantes.
Autentique-se usando o JWT gerado na rota /api/token/.

**Provas e Questões:**
Crie provas e associe questões e opções.
Use as rotas de listagem para validar paginação, busca e ordenação.

**Respostas e Participação:**
Inscreva participantes em provas.
Envie respostas e finalize a prova para calcular rankings.


**Cache**:
Valide o cache nos endpoints de listagem (ex.: /api/exams/).

**Tarefas Assíncronas**:
Confirme que tarefas como correção de respostas e cálculo de rankings são executadas corretamente por meio do Celery e Redis.


## Funcionalidades Implementadas
 - Autenticação JWT para acesso seguro.
 - Gerenciamento de entidades como usuários, provas, questões e respostas.
 - Correção assíncrona de respostas e cálculo de rankings.
 - Caching em endpoints críticos para melhorar desempenho.
 - Paginação, ordenação e busca nos endpoints.
 - Documentação Interativa com Django Ninja.

## Tecnologias Utilizadas
 - Django Ninja para APIs rápidas e eficientes.
 - Redis para caching e suporte ao Celery.
 - Celery para tarefas assíncronas.
 - Poetry para gerenciamento de dependências.
 - Docker e Docker Compose para containerização.

## Para rodar os testes unitários
`python manage.py test api.tests`

## Para visualizar documentação, basta executar o projeto via docker e acessar a rota:
[http://127.0.0.1:8000/api/docs](Documentaçãos)