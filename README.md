# desafio_django
Desenvolvimento de uma Web Service RESTful para gerenciamento de provas com questões de múltiplas escolhas. 

# Para executar o projeto via Docker, todos os comandos necessários para a inicialização da aplicação no servidor serão executados, incluindo instalação de dependências via poetry. Basta executar os comandos:
docker-compose build
docker-compose up

# Crie um superusuário em outro terminal com o servidor rodando
python manage.py createsuperuser

# Autentique-o via Insomnia ou Postman passando username e senha no corpo da requisição feita para a rota http://127.0.0.1:8000/api/token/ ou apenas acessando a rota e passando os parâmetros no formulário gerado automaticamente pelo DRF

# Para rodar os testes unitários
python manage.py test api.tests

# Para visualizar documentação, basta executar o projeto via docker e acessar a rota:
http://127.0.0.1:8000/api/docs 
