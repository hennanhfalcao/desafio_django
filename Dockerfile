FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Instalação do Poetry e dependências
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create true && poetry install --no-dev

# Copia os arquivos do projeto
COPY . .

# Comando padrão
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
