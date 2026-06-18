FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

# Default command overridden by docker-compose
CMD ["uvicorn", "app.auth.main:app", "--host", "0.0.0.0", "--port", "8001"]