# Dockerfile

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 1) System deps for building Python packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# 2) Install Poetry CLI
RUN pip install --upgrade pip poetry

# 3) Copy only lockfiles, install dependencies
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# 4) Copy your entire codebase
COPY . /app/

# 5) Collect static assets (WhiteNoise will serve them)
RUN python manage.py collectstatic --noinput

# 4) Expose port & start Gunicorn + WhiteNoise
ENV STATIC_URL=/static/
ENV STATIC_ROOT=/app/staticfiles
ENV DJANGO_SETTINGS_MODULE=config.settings

# 6) Expose port and switch to a production WSGI server
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]