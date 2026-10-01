FROM python:3.14-slim

WORKDIR /app

# psycopg2 (not the -binary wheel-only path on every platform) needs libpq + a compiler
# to build from source; installing these keeps the image working even if a prebuilt
# wheel isn't available for this base image's platform/Python combo.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
