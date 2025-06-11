# Dockerfile para Compositor de Música Católica
FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para dados
RUN mkdir -p /app/data

# Expor porta
EXPOSE 8501

# Configurar variáveis de ambiente
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Verificação de saúde
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando para executar a aplicação
CMD ["streamlit", "run", "AgentCompose.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
