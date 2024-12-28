FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* ./

RUN /root/.local/bin/poetry config virtualenvs.create false

RUN /root/.local/bin/poetry install --no-interaction --no-root

COPY . .

RUN /root/.local/bin/poetry install --no-interaction


FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
