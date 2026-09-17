FROM python:3.13-slim

WORKDIR /app

COPY api/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/

RUN groupadd --system appgroup \
    && useradd --system --gid appgroup appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]