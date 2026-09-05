FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


RUN useradd \
    --create-home \
    --uid 10001 \
    appuser


COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --upgrade pip \
    && pip install \
    --no-cache-dir \
    -r requirements.txt


COPY app ./app


RUN chown -R appuser:appuser /app

USER 10001


EXPOSE 8002


CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8002"]