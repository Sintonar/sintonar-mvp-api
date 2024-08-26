FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências para o contêiner
COPY requirements.txt /app/

# Instala as dependências da aplicação
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o contêiner
COPY . /app/

COPY .env /app/

# Configura as variáveis de ambiente para produção
ENV DJANGO_SETTINGS_MODULE=sintonar.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random

# Exponha a porta que será usada pela aplicação
EXPOSE 8000

# Comando para rodar a aplicação Django usando gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "sintonar.wsgi:application", "--workers", "3"]