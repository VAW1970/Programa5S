FROM python:3.12-slim

LABEL maintainer="Programa 5S"
LABEL description="Sistema de Gerenciamento de Auditorias 5S"

# Criar usuario nao-root por seguranca
RUN useradd --create-home --shell /bin/bash appuser

# Definir diretorio de trabalho
WORKDIR /app

# Instalar dependencias primeiro (melhor cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo da aplicacao
COPY . .

# Criar diretorio para o banco de dados
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Trocar para usuario nao-root
USER appuser

# Expor porta
EXPOSE 5000

# Variavel de ambiente para o banco de dados
ENV DATABASE=/app/data/auditoria_5s.db

# Comando para iniciar a aplicacao
CMD ["python", "app.py"]
