FROM python:3.11-slim

WORKDIR /app

# Увеличиваем таймауты (без зеркала)
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_RETRIES=10

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install fastapi uvicorn[standard]
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /app/data

RUN python -c "import uvicorn; print('uvicorn installed successfully')"

EXPOSE 8000

# Запускаем init_db.py перед стартом сервера
CMD ["python", "init_db.py"]

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
