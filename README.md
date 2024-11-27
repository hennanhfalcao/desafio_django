# desafio_django
Desenvolvimento de uma Web Service RESTful para gerenciamento de provas com questões de múltiplas escolhas. 

# Criar o ambiente virtual
python3 -m venv .venv

# Ativar o ambiente virtual (Linux/macOS)
source venv/bin/activate

# Ativar o ambiente virtual (Windows)
.venv\Scripts\activate

# Instalar as dependências usando o Poetry
poetry install

# Rodar o servidor Django sem o Docker
poetry run python manage.py runserver

# Para executar as migrações sem o docker
python manage.py makemigrations
python manage.py migrate

# Para executar o projeto via Docker
docker-compose build
docker-compose up

# Executar as migrações localmente caso a pasta migrations não esteja presente
docker-compose exec web python manage.py makemigrations api
docker-compose exec web python manage.py migrate

# Para rodar os testes unitários
python manage.py test api.tests