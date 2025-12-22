FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV DJANGO_SETTINGS_MODULE=tcc.settings

WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        build-essential \
        gcc \
        python3-dev \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libbz2-dev \
        liblzma-dev \
        pkg-config \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY tcc/requirements.txt /app/requirements.txt
# Remove Windows-only packages (pywin32) from requirements before installing
RUN pip install --upgrade pip setuptools wheel \
    && sed -E '/^pywin32(==.*)?$/Id' /app/requirements.txt > /app/requirements.filtered.txt \
    && pip install --no-cache-dir -r /app/requirements.filtered.txt \
    && pip install --no-cache-dir gunicorn

# Copy project
COPY tcc /app

# Entrypoint script will run migrations and collectstatic before starting the server
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "tcc.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]