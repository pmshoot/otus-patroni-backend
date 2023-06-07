# Простой сервер на fastAPI для создания бекенда к postgresql для проведения тестирования кластера при нагрузке yandex tank
# pre build
FROM python:3.9 as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# final step
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY main.py .

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0",  "--reload"]
