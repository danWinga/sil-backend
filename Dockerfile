# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# 1) Install system deps if any
RUN apt-get update \
    && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2) Install Python deps via Poetry
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 3) Copy code & collect static
COPY . .
RUN python manage.py collectstatic --noinput

# 4) Expose port & start Gunicorn + WhiteNoise
ENV STATIC_URL=/static/
ENV STATIC_ROOT=/app/staticfiles
ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]