FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
# Optional environment file (will not exist in clean context). Use a dummy if absent.
ONBUILD ARG DUMMY_ENV=1
RUN touch .env

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
