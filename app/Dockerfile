# Use a imagem base do Python
FROM python:3.9

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos necessários para o diretório de trabalho
COPY . .

# Instala as dependências do Python
RUN pip install -r requirements.txt

# Expõe a porta que a aplicação FastAPI irá usar
EXPOSE 8000

# Comando para iniciar a aplicação FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
