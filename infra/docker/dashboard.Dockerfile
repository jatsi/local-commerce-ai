FROM python:3.11-slim

WORKDIR /app
COPY apps/dashboard /app/apps/dashboard

CMD ["python", "-m", "http.server", "3000", "-d", "/app/apps/dashboard"]
