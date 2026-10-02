FROM python:3.11-slim

WORKDIR /app

# Встановлюємо системні залежності для збірки psycopg2 (роботи з Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо бібліотеки Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту в контейнер
COPY . .

EXPOSE 8000