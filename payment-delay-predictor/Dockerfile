FROM python:3.12-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Apply current Debian security updates, then remove
# package-manager metadata from the final image layer.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Install application dependencies before copying source
# so dependency layers remain cacheable.
COPY requirements-api.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-api.txt

# Create an unprivileged runtime identity.
RUN groupadd --gid 10001 appgroup \
    && useradd \
        --uid 10001 \
        --gid appgroup \
        --create-home \
        --shell /usr/sbin/nologin \
        appuser

COPY --chown=appuser:appgroup app ./app

COPY --chown=appuser:appgroup \
    artifacts/logistic-regression-v1 \
    ./artifacts/logistic-regression-v1

COPY --chown=appuser:appgroup \
    artifacts/explainability/logistic-regression-v1 \
    ./artifacts/explainability/logistic-regression-v1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
