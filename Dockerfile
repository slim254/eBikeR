FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY ebikeRent/frontend/package*.json ./
RUN npm install
COPY ebikeRent/frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ebikeRent/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ebikeRent/backend/ ./
COPY --from=frontend-build /app/frontend/dist /app/static/frontend

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
