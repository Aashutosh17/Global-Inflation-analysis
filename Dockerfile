FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard ./dashboard
COPY data ./data

ENV HOST=0.0.0.0
ENV PORT=8050

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} dashboard.run_dashboard:server"]
