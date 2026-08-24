FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN pip install --no-cache-dir "numpy>=2.0,<3"

COPY scripts/ /app/scripts/

EXPOSE 8765

CMD ["python", "-m", "scripts.archive_chat", "--host", "0.0.0.0", "--port", "8765", "--llm", "--retrieval", "vector"]
