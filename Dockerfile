FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

WORKDIR /app

# Install prerequisites for adding PostgreSQL repository
RUN apt-get update && apt-get install -y wget gnupg2 lsb-release

# Add PostgreSQL repository and install PostgreSQL client 16
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && \
    apt-get install -y postgresql-client-16

# Install other dependencies
RUN apt-get install -y \
    python3-pip \
    python3 \
    build-essential \
    libpq-dev \
    libmagic-dev \
    poppler-utils \
    libxml2-dev \
    libxslt1-dev \
    libreoffice \
    pandoc \
    libgeos-c1v5 \
    libgeos-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libpng-dev \
    libmupdf-dev \
    pkg-config \
    libhdf5-dev

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# CMD [ "uvicorn app.main:app --host 0.0.0.0 --port 8001" ]
