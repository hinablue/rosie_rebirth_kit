FROM node:24-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ARCHIVE_CHAT_STATIC_ROOT=/app/static

WORKDIR /app

RUN pip install --no-cache-dir "numpy>=2.0,<3"

COPY scripts/ /app/scripts/
COPY --from=frontend-build /frontend/dist/ /app/static/

EXPOSE 8765

CMD ["python", "-m", "scripts.archive_chat", "--host", "0.0.0.0", "--port", "8765", "--llm", "--retrieval", "vector"]
