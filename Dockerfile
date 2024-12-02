FROM python:3.10

# Define o diretório de trabalho
WORKDIR /app

# Instala o Poetry
RUN pip install poetry

# Copia os arquivos de dependência primeiro para evitar reinstalações desnecessárias
COPY pyproject.toml poetry.lock ./

# Instala as dependências do projeto sem criar um ambiente virtual
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

# Copia o restante dos arquivos do projeto
COPY . .

# Comando padrão para iniciar o servidor
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]