FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-common gnupg2 lsb-release curl && \
    yes | /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh && \
    apt-get install -y --no-install-recommends postgresql-16 postgresql-client-16 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir --default-timeout=300 --retries=5 .
RUN pip install --no-cache-dir psycopg2-binary "bcrypt==4.1.3"

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini ./
COPY scripts/ scripts/
COPY start.sh ./
RUN chmod +x start.sh

ENV DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/voice_agent
ENV DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/voice_agent
ENV CHROMA_HOST=localhost
ENV CHROMA_PORT=8100
ENV PYTHONPATH=/app

RUN echo "local all all trust" > /etc/postgresql/16/main/pg_hba.conf && \
    echo "host all all 127.0.0.1/32 trust" >> /etc/postgresql/16/main/pg_hba.conf && \
    echo "host all all ::1/128 trust" >> /etc/postgresql/16/main/pg_hba.conf

EXPOSE 8000

CMD ["./start.sh"]
