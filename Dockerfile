# Dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 1) System deps for building Python packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      curl \
 && rm -rf /var/lib/apt/lists/*

# 2) Install Poetry CLI
RUN pip install --upgrade pip poetry

# 3) Copy only lockfiles, install dependencies (no-root)
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# 4) Copy your entire codebase
COPY . /app/

COPY . .

# Collect static into ./staticfiles
RUN python manage.py collectstatic --noinpu

EXPOSE 8000

# 5) Default command for web (overridden in compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Default: run migrations then Django server
#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]