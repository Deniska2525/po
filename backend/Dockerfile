FROM python:3.11-slim

WORKDIR /app

# Увеличиваем таймауты (без зеркала)
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_RETRIES=10

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install fastapi uvicorn[standard]
RUN pip install --no-cache-dir --timeout 100 --retries 10 -r requirements.txt

COPY . .
RUN mkdir -p /app/data

RUN python -c "import uvicorn; print('uvicorn installed successfully')"
RUN python init_db.py 

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
