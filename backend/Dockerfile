FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_NAME="Behavioral Monitor API" \
    DEBUG=false \
    HOST=0.0.0.0 \
    PORT=8765 \
    ARTIFACTS_DIR=/app/artifacts

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/artifacts

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765", "--workers", "1"]
