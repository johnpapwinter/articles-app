FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libpq-dev \
        pkg-config \
        python3-dev \
        postgresql-client \
        python3-psycopg \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* ./

RUN /root/.local/bin/poetry config virtualenvs.create false

RUN /root/.local/bin/poetry install --no-interaction --no-root

COPY . .

RUN /root/.local/bin/poetry install --no-interaction


FROM python:3.12-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        postgresql-client \
        python3-psycopg \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages and application
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app .

# Create __init__.py if it doesn't exist
RUN touch /app/__init__.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]