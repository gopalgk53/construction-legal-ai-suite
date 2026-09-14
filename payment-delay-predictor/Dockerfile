FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-api.txt .

RUN pip install --upgrade pip && pip install -r requirements-api.txt

COPY app ./app

COPY artifacts/logistic-regression-v1 ./artifacts/logistic-regression-v1

COPY artifacts/explainability/logistic-regression-v1 ./artifacts/explainability/logistic-regression-v1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
